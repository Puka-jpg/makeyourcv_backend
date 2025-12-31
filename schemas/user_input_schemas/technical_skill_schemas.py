from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, TimestampSchema


class TechnicalSkillBaseSchema(BaseModel):
    """Base schema for technical skill"""

    category: str
    skills: List[str]


class TechnicalSkillCreateSchema(TechnicalSkillBaseSchema, ContentBaseSchema):
    """Schema for creating technical skill"""

    pass


class TechnicalSkillUpdateSchema(BaseModel):
    """Schema for updating technical skill - all fields optional"""

    category: Optional[str] = None
    skills: Optional[List[str]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class TechnicalSkillResponseSchema(
    TechnicalSkillBaseSchema, ContentBaseSchema, TimestampSchema
):
    """Schema for technical skill responses"""

    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
