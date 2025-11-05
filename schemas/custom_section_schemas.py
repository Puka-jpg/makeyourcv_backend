from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class CustomSectionBaseSchema(BaseModel):
    """Base schema for custom section"""

    section_title: str
    content: str


class CustomSectionCreateSchema(CustomSectionBaseSchema, ContentBaseSchema):
    """Schema for creating custom section"""

    user_id: int


class CustomSectionUpdateSchema(BaseModel):
    """Schema for updating custom section - all fields optional"""

    section_title: Optional[str] = None
    content: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CustomSectionResponseSchema(
    CustomSectionBaseSchema,
    ContentBaseSchema,
    TimestampSchema,
    EnhancementMetadataSchema,
):
    """Schema for custom section responses"""

    id: int
    user_id: int
    content_enhanced: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
