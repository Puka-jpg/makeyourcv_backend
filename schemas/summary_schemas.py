from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.common import EnhancementMetadataSchema, TimestampSchema


class SummaryBaseSchema(BaseModel):
    """Base schema for summary"""

    summary_text: str


class SummaryCreateSchema(SummaryBaseSchema):
    """Schema for creating a summary"""

    user_id: int


class SummaryUpdateSchema(BaseModel):
    """Schema for updating a summary - all fields optional"""

    summary_text: Optional[str] = None


class SummaryResponseSchema(
    SummaryBaseSchema, TimestampSchema, EnhancementMetadataSchema
):
    """Schema for summary responses"""

    id: int
    user_id: int
    summary_enhanced: Optional[str] = None
    is_ai_generated: bool = False

    model_config = ConfigDict(from_attributes=True)
