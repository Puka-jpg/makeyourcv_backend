from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user_schemas import UserCreateSchema, UserUpdateSchema


class UserOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, payload: UserCreateSchema) -> User:
        """Create a new user in the database"""
        user = User(username=payload.username, email=payload.email)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve all users with pagination"""
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        return list(users)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a single user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username"""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def update_user(
        self, user_id: int, payload: UserUpdateSchema
    ) -> Optional[User]:
        """Update an existing user"""
        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        # Update only the fields that are provided
        if payload.username is not None:
            user.username = payload.username

        if payload.email is not None:
            user.email = payload.email

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID (cascades to all related data)"""
        user = await self.get_user_by_id(user_id)

        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def user_exists(
        self, username: Optional[str] = None, email: Optional[str] = None
    ) -> bool:
        """Check if a user exists by username or email"""
        if username:
            user = await self.get_user_by_username(username)
            if user:
                return True

        if email:
            user = await self.get_user_by_email(email)
            if user:
                return True

        return False
