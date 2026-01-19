from datetime import date
from typing import Optional
from uuid import UUID

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

    pass


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

    id: UUID
    user_id: UUID
    description_enhanced: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
