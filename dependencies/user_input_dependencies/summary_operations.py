from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Summary
from schemas.user_input_schemas.summary_schemas import (
    SummaryCreateSchema,
    SummaryUpdateSchema,
)


class SummaryOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_summary(
        self, payload: SummaryCreateSchema, user_id: UUID
    ) -> Summary:
        """Create a summary in the database"""
        summary = Summary(
            user_id=user_id,
            summary_text=payload.summary_text,
            summary_enhanced=None,  # Placeholder for AI enhancement
            is_ai_generated=False,
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        return summary

    async def get_summary_by_id(
        self, summary_id: UUID, user_id: UUID
    ) -> Optional[Summary]:
        """Retrieve summary by ID"""
        query = select(Summary).where(
            Summary.id == summary_id, Summary.user_id == user_id
        )
        result = await self.db.execute(query)
        summary = result.scalar_one_or_none()
        return summary

    async def get_summary_by_user_id(self, user_id: UUID) -> Optional[Summary]:
        """Retrieve summary by User ID (1-to-1)"""
        query = select(Summary).where(Summary.user_id == user_id)
        result = await self.db.execute(query)
        summary = result.scalar_one_or_none()
        return summary

    async def update_summary(
        self, summary_id: UUID, user_id: UUID, payload: SummaryUpdateSchema
    ) -> Optional[Summary]:
        """Update existing summary"""
        summary = await self.get_summary_by_id(summary_id, user_id)

        if not summary:
            return None

        if payload.summary_text is not None:
            summary.summary_text = payload.summary_text

        await self.db.commit()
        await self.db.refresh(summary)
        return summary

    async def update_summary_by_user(
        self, user_id: UUID, payload: SummaryUpdateSchema
    ) -> Optional[Summary]:
        """Update existing summary for a user"""
        summary = await self.get_summary_by_user_id(user_id)

        if not summary:
            return None

        if payload.summary_text is not None:
            summary.summary_text = payload.summary_text

        await self.db.commit()
        await self.db.refresh(summary)
        return summary

    async def delete_summary(self, summary_id: UUID, user_id: UUID) -> bool:
        """Delete summary by ID"""
        summary = await self.get_summary_by_id(summary_id, user_id)

        if not summary:
            return False

        await self.db.delete(summary)
        await self.db.commit()
        return True

    async def delete_summary_by_user(self, user_id: UUID) -> bool:
        """Delete summary by User ID"""
        summary = await self.get_summary_by_user_id(user_id)

        if not summary:
            return False

        await self.db.delete(summary)
        await self.db.commit()
        return True
