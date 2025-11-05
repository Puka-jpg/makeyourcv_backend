from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import ContentBaseSchema, EnhancementMetadataSchema, TimestampSchema


class CertificationBaseSchema(BaseModel):
    """Base schema for certification"""

    certification_name: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    description: Optional[str] = None


class CertificationCreateSchema(CertificationBaseSchema, ContentBaseSchema):
    """Schema for creating certification"""

    user_id: int


class CertificationUpdateSchema(BaseModel):
    """Schema for updating certification - all fields optional"""

    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CertificationResponseSchema(
    CertificationBaseSchema,
    ContentBaseSchema,
    TimestampSchema,
    EnhancementMetadataSchema,
):
    """Schema for certification responses"""

    id: int
    user_id: int
    description_enhanced: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
