from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseSchema(BaseModel):
    """Base schema with common user fields"""

    username: str
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a new user"""

    pass


class UserUpdateSchema(BaseModel):
    """Schema for updating a user - all fields optional"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponseSchema(UserBaseSchema):
    """Schema for user responses - includes ID and metadata"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
