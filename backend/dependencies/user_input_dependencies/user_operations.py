from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user_input_schemas.user_schemas import UserUpdateSchema


class UserOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a single user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def update_user(self, user: User, payload: UserUpdateSchema) -> User:
        """Update an existing user"""
        # Update only the fields that are provided
        if payload.username is not None:
            user.first_name = payload.username

        if payload.email is not None:
            user.email = payload.email

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: User) -> bool:
        """Delete a user object"""
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def user_exists(
        self, username: Optional[str] = None, email: Optional[str] = None
    ) -> bool:
        """Check if a user exists by username (first_name) or email"""
        if username:
            query = select(User).where(User.first_name == username)
            result = await self.db.execute(query)
            if result.scalar_one_or_none():
                return True

        if email:
            if await self.get_user_by_email(email):
                return True

        return False
