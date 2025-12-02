from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class PublicationBaseSchema(BaseModel):
    """Base schema for publication"""

    title: str
    authors: Optional[str] = None
    publication_venue: Optional[str] = None
    publication_date: Optional[date] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class PublicationCreateSchema(PublicationBaseSchema, ContentBaseSchema):
    """Schema for creating publication"""

    user_id: int


class PublicationUpdateSchema(BaseModel):
    """Schema for updating publication - all fields optional"""

    title: Optional[str] = None
    authors: Optional[str] = None
    publication_venue: Optional[str] = None
    publication_date: Optional[date] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class PublicationResponseSchema(
    PublicationBaseSchema, ContentBaseSchema, TimestampSchema, EnhancementMetadataSchema
):
    """Schema for publication responses"""

    id: int
    user_id: int
    description_enhanced: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
