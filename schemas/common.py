from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ErrorResponseSchema(BaseModel):
    detail: str


# Base schemas for reusability
class TimestampSchema(BaseModel):
    """Timestamp fields for responses"""

    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentBaseSchema(BaseModel):
    """Base for content with display ordering"""

    display_order: int = 0
    is_active: bool = True


class EnhancementMetadataSchema(BaseModel):
    """AI enhancement tracking metadata"""

    enhancement_prompt_used: Optional[str] = None
    last_enhanced_at: Optional[datetime] = None
