from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class EducationBaseSchema(BaseModel):
    """Base schema for education"""

    institution_name: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    grade: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class EducationCreateSchema(EducationBaseSchema, ContentBaseSchema):
    """Schema for creating education"""

    user_id: int


class EducationUpdateSchema(BaseModel):
    """Schema for updating education - all fields optional"""

    institution_name: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    grade: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class EducationResponseSchema(
    EducationBaseSchema, ContentBaseSchema, TimestampSchema, EnhancementMetadataSchema
):
    """Schema for education responses"""

    id: int
    user_id: int
    description_enhanced: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
