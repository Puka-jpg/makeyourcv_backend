from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Education
from schemas.user_input_schemas.education_schemas import (
    EducationCreateSchema,
    EducationUpdateSchema,
)


class EducationOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_education(
        self, payload: EducationCreateSchema, user_id: UUID
    ) -> Education:
        """Create education in the database"""
        education = Education(
            user_id=user_id,
            institution_name=payload.institution_name,
            degree=payload.degree,
            field_of_study=payload.field_of_study,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            grade=payload.grade,
            location=payload.location,
            description=payload.description,
            description_enhanced=None,  # Placeholder for AI
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(education)
        await self.db.commit()
        await self.db.refresh(education)
        return education

    async def get_all_education(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Education]:
        """Retrieve all education for a user"""
        query = (
            select(Education)
            .where(Education.user_id == user_id)
            .order_by(Education.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        education_list = result.scalars().all()
        return list(education_list)

    async def get_education_by_id(
        self, education_id: UUID, user_id: UUID
    ) -> Optional[Education]:
        """Retrieve single education by ID"""
        query = select(Education).where(
            Education.id == education_id, Education.user_id == user_id
        )
        result = await self.db.execute(query)
        education = result.scalar_one_or_none()
        return education

    async def update_education(
        self,
        education_id: UUID,
        payload: EducationUpdateSchema,
        user_id: UUID,
    ) -> Optional[Education]:
        """Update existing education"""
        education = await self.get_education_by_id(education_id, user_id)

        if not education:
            return None

        if payload.institution_name is not None:
            education.institution_name = payload.institution_name
        if payload.degree is not None:
            education.degree = payload.degree
        if payload.field_of_study is not None:
            education.field_of_study = payload.field_of_study
        if payload.start_date is not None:
            education.start_date = payload.start_date
        if payload.end_date is not None:
            education.end_date = payload.end_date
        if payload.is_current is not None:
            education.is_current = payload.is_current
        if payload.grade is not None:
            education.grade = payload.grade
        if payload.location is not None:
            education.location = payload.location
        if payload.description is not None:
            education.description = payload.description
        if payload.display_order is not None:
            education.display_order = payload.display_order
        if payload.is_active is not None:
            education.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(education)
        return education

    async def delete_education(self, education_id: UUID, user_id: UUID) -> bool:
        """Delete education by ID"""
        education = await self.get_education_by_id(education_id, user_id)

        if not education:
            return False

        await self.db.delete(education)
        await self.db.commit()
        return True
