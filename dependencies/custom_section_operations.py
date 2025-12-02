from typing import List, Optional

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
        self, payload: CustomSectionCreateSchema
    ) -> CustomSection:
        """Create custom section in the database"""
        custom_section = CustomSection(
            user_id=payload.user_id,
            section_title=payload.section_title,
            content=payload.content,
            content_enhanced=None,  # Placeholder for AI
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(custom_section)
        await self.db.commit()
        await self.db.refresh(custom_section)
        return custom_section

    async def get_all_custom_sections(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[CustomSection]:
        """Retrieve all custom sections for a user"""
        query = (
            select(CustomSection)
            .where(CustomSection.user_id == user_id)
            .order_by(CustomSection.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        sections = result.scalars().all()
        return list(sections)

    async def get_custom_section_by_id(
        self, section_id: int, user_id: int
    ) -> Optional[CustomSection]:
        """Retrieve single custom section by ID"""
        query = select(CustomSection).where(
            CustomSection.id == section_id, CustomSection.user_id == user_id
        )
        result = await self.db.execute(query)
        section = result.scalar_one_or_none()
        return section

    async def update_custom_section(
        self, section_id: int, user_id: int, payload: CustomSectionUpdateSchema
    ) -> Optional[CustomSection]:
        """Update existing custom section"""
        section = await self.get_custom_section_by_id(section_id, user_id)

        if not section:
            return None

        if payload.section_title is not None:
            section.section_title = payload.section_title
        if payload.content is not None:
            section.content = payload.content
        if payload.display_order is not None:
            section.display_order = payload.display_order
        if payload.is_active is not None:
            section.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def delete_custom_section(self, section_id: int, user_id: int) -> bool:
        """Delete custom section by ID"""
        section = await self.get_custom_section_by_id(section_id, user_id)

        if not section:
            return False

        await self.db.delete(section)
        await self.db.commit()
        return True
