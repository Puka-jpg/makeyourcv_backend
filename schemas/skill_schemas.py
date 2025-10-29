from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SkillBaseSchema(BaseModel):
    """Base schema with common fields"""

    skill_name: str
    skill_description: str


class SkillCreateSchema(SkillBaseSchema):
    """Schema for creating a new skill"""

    pass


class SkillUpdateSchema(BaseModel):
    """Schema for updating an existing skill - all fields optional"""

    skill_name: Optional[str]
    skill_description: Optional[str]


class SkillResponseSchema(SkillBaseSchema):
    """Schema for skill responses - includes ID and metadata"""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SkillListResponseSchema(BaseModel):
    """Schema for listing multiple skills with metadata"""

    total: int
    skills: list[SkillResponseSchema]

    model_config = ConfigDict(from_attributes=True)
