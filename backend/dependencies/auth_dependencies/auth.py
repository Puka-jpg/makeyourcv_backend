import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import RefreshToken, User
from schemas.auth_schemas.auth import (
    LoginInputSchema,
    LoginOutputSchema,
    RefreshTokenSchema,
    SignupInputSchema,
)
from schemas.common import ErrorResponseSchema
from settings import settings
from utils.helpers import hash_password, verify_password
from utils.logger import get_logger

logger = get_logger()
security = HTTPBearer()


class Auth:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def signup(self, payload: SignupInputSchema) -> Response:
        try:
            user = User(
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=payload.email,
                hashed_password=hash_password(payload.password),
            )
            self.db.add(user)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponseSchema(detail="Email already exists").model_dump(),
            )
        return Response(status_code=status.HTTP_201_CREATED)

    async def login(self, payload: LoginInputSchema):
        result = await self.db.execute(select(User).where(User.email == payload.email))
        if (user := result.fetchone()) is None or verify_password(
            user[0].hashed_password, payload.password
        ) is False:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponseSchema(
                    detail="Invalid email or password"
                ).model_dump(),
            )
        # Generate access and refresh token
        tokens = await self._generate_token_pair(user[0])
        return JSONResponse(status_code=status.HTTP_200_OK, content=tokens.model_dump())

    async def _generate_token_pair(self, user: User) -> LoginOutputSchema:
        jti: uuid.UUID = uuid.uuid4()
        access_token = await self._generate_access_token(str(user.id), jti)
        refresh_token = await self._generate_refresh_token(str(user.id), jti)
        # Store the refresh token in db
        refresh_token_retry = RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.JWT_REFRESH_EXPIRATION_MINUTES),
        )
        self.db.add(refresh_token_retry)
        await self.db.commit()
        logger.info("Token pair generated", extra={"user_id": str(user.id)})
        return LoginOutputSchema(access=access_token, refresh=refresh_token)

    async def _generate_refresh_token(self, user_id: str, jti: uuid.UUID) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.JWT_REFRESH_EXPIRATION_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
            "jti": str(jti),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    async def _generate_access_token(self, user_id: str, jti: uuid.UUID) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
            "jti": str(jti),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    async def refresh(self, payload: RefreshTokenSchema) -> JSONResponse:
        try:
            current_token = jwt.decode(
                payload.refresh, settings.JWT_SECRET, algorithms=["HS256"]
            )
            if current_token.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            user_id = current_token.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not contain subject",
                )
            jti = current_token.get("jti")
            if not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not contain jti",
                )
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.unique().scalar_one_or_none()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )
            current_tokens = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user.id,
                    RefreshToken.jti == jti,
                    RefreshToken.is_blacklisted == False,  # noqa: E712
                )
            )
            cts = current_tokens.scalars().all()
            if not cts:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not found or blacklisted",
                )
            for ct in cts:
                ct.is_blacklisted = True
            await self.db.commit()
            # Generate new access and refresh tokens
            new_tokens = await self._generate_token_pair(user)
            logger.info(
                "Tokens refreshed successfully",
                extra={"user_id": str(user.id), "jti": str(jti)},
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=new_tokens.model_dump(),
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    async def logout(self, payload: RefreshTokenSchema) -> Response:
        try:
            current_token = jwt.decode(
                payload.refresh, settings.JWT_SECRET, algorithms=["HS256"]
            )
            if current_token.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="invalid token type",
                )
            user_id = current_token.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not contain subject",
                )
            jti = current_token.get("jti")
            if not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not contain jti",
                )
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.unique().scalar_one_or_none()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )
            current_tokens = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user.id,
                    RefreshToken.jti == jti,
                    RefreshToken.is_blacklisted == False,  # noqa: E712
                )
            )
            cts = current_tokens.scalars().all()
            if not cts:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not found or blacklisted",
                )
            for ct in cts:
                ct.is_blacklisted = True
            await self.db.commit()
            logger.info("User logged out successfully", extra={"user_id": str(user.id)})
            # Return 204 No Content response
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain subject",
            )
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
