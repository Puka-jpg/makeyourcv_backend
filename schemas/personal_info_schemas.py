from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class PersonalInfoBaseSchema(BaseModel):
    """Base schema with common personal info fields"""

    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    professional_title: Optional[str] = None


class PersonalInfoCreateSchema(PersonalInfoBaseSchema):
    """Schema for creating personal info"""

    user_id: int


class PersonalInfoUpdateSchema(BaseModel):
    """Schema for updating personal info - all fields optional"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None
    professional_title: Optional[str] = None


class PersonalInfoResponseSchema(PersonalInfoBaseSchema):
    """Schema for personal info responses - includes ID and metadata"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
