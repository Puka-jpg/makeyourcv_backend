from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class ExperienceBaseSchema(BaseModel):
    """Base schema for experience"""

    job_title: str
    company_name: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    technologies_used: Optional[List[str]] = None


class ExperienceCreateSchema(ExperienceBaseSchema, ContentBaseSchema):
    """Schema for creating experience"""

    pass


class ExperienceUpdateSchema(BaseModel):
    """Schema for updating experience - all fields optional"""

    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    technologies_used: Optional[List[str]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ExperienceResponseSchema(
    ExperienceBaseSchema, ContentBaseSchema, TimestampSchema, EnhancementMetadataSchema
):
    """Schema for experience responses"""

    id: UUID
    user_id: UUID
    description_enhanced: Optional[str] = None
    achievements_enhanced: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
