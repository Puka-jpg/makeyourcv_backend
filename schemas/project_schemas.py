from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class ProjectBaseSchema(BaseModel):
    """Base schema for project"""

    project_name: str
    description: str
    highlights: Optional[List[str]] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    technologies_used: Optional[List[str]] = None
    is_featured: bool = False


class ProjectCreateSchema(ProjectBaseSchema, ContentBaseSchema):
    """Schema for creating project"""

    user_id: int


class ProjectUpdateSchema(BaseModel):
    """Schema for updating project - all fields optional"""

    project_name: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[List[str]] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    technologies_used: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ProjectResponseSchema(
    ProjectBaseSchema, ContentBaseSchema, TimestampSchema, EnhancementMetadataSchema
):
    """Schema for project responses"""

    id: int
    user_id: int
    description_enhanced: Optional[str] = None
    highlights_enhanced: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
