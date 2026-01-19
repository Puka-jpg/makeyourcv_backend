from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from dependencies.auth_dependencies.auth import Auth
from schemas.auth_schemas.auth import (
    LoginInputSchema,
    LoginOutputSchema,
    RefreshTokenSchema,
    SignupInputSchema,
)
from schemas.common import ErrorResponseSchema
from utils.logger import get_logger

logger = get_logger()


router = APIRouter()


@router.post(
    path="/signup",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description=": "User created successfully"},
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponseSchema,
            "description": "Email already exists",
        },
    },
)
async def signup(
    payload: SignupInputSchema,
    auth: Annotated[Auth, Depends(Auth)],
) -> Response:
    res = await auth.signup(payload)
    logger.info("User Created cussessfuly", extra={"email": payload.email})
    return res


@router.post(
    path="/login",
    responses={
        status.HTTP_200_OK: {
            "model": LoginOutputSchema,
            "description": "Login successful",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponseSchema,
            "description": "Invalid credentials",
        },
    },
)
async def login(
    payload: LoginInputSchema, auth: Annotated[Auth, Depends(Auth)]
) -> Response:
    return await auth.login(payload)


@router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Logout successful"},
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponseSchema,
            "description": "Invalid refresh token",
        },
    },
)
async def logout(
    payload: RefreshTokenSchema, auth: Annotated[Auth, Depends(Auth)]
) -> Response:
    return await auth.logout(payload)
