from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CustomSection
from schemas.user_input_schemas.custom_section_schemas import (
    CustomSectionCreateSchema,
    CustomSectionUpdateSchema,
)


class CustomSectionOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_custom_section(
        self, payload: CustomSectionCreateSchema, user_id: UUID
    ) -> CustomSection:
        """Create a new custom section"""
        custom_section = CustomSection(
            user_id=user_id,
            section_title=payload.section_title,
            content=payload.content,
            content_enhanced=None,
        )
        self.db.add(custom_section)
        await self.db.commit()
        await self.db.refresh(custom_section)
        return custom_section

    async def get_all_custom_sections(self, user_id: UUID) -> List[CustomSection]:
        """Retrieve all custom sections for a user"""
        query = select(CustomSection).where(CustomSection.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_custom_section_by_id(
        self, section_id: UUID, user_id: UUID
    ) -> Optional[CustomSection]:
        """Retrieve a single custom section by ID"""
        query = select(CustomSection).where(
            CustomSection.id == section_id, CustomSection.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_custom_section(
        self, section_id: UUID, user_id: UUID, payload: CustomSectionUpdateSchema
    ) -> Optional[CustomSection]:
        """Update existing custom section"""
        custom_section = await self.get_custom_section_by_id(section_id, user_id)
        if not custom_section:
            return None

        if payload.section_title is not None:
            custom_section.section_title = payload.section_title

        if payload.content is not None:
            custom_section.content = payload.content

        await self.db.commit()
        await self.db.refresh(custom_section)
        return custom_section

    async def delete_custom_section(self, section_id: UUID, user_id: UUID) -> bool:
        """Delete custom section"""
        custom_section = await self.get_custom_section_by_id(section_id, user_id)

        if not custom_section:
            return False

        await self.db.delete(custom_section)
        await self.db.commit()
        return True
