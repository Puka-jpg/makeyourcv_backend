from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Experience
from schemas.user_input_schemas.experience_schemas import (
    ExperienceCreateSchema,
    ExperienceUpdateSchema,
)


class ExperienceOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experience(self, payload: ExperienceCreateSchema) -> Experience:
        """Create experience in the database"""
        experience = Experience(
            user_id=payload.user_id,
            job_title=payload.job_title,
            company_name=payload.company_name,
            location=payload.location,
            employment_type=payload.employment_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            is_current=payload.is_current,
            description=payload.description,
            achievements=payload.achievements,
            description_enhanced=None,  # Placeholder for AI
            achievements_enhanced=None,  # Placeholder for AI
            technologies_used=payload.technologies_used,
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(experience)
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

    async def get_all_experiences(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Experience]:
        """Retrieve all experiences for a user"""
        query = (
            select(Experience)
            .where(Experience.user_id == user_id)
            .order_by(Experience.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        experiences = result.scalars().all()
        return list(experiences)

    async def get_experience_by_id(
        self, experience_id: int, user_id: int
    ) -> Optional[Experience]:
        """Retrieve single experience by ID"""
        query = select(Experience).where(
            Experience.id == experience_id, Experience.user_id == user_id
        )
        result = await self.db.execute(query)
        experience = result.scalar_one_or_none()
        return experience

    async def update_experience(
        self, experience_id: int, user_id: int, payload: ExperienceUpdateSchema
    ) -> Optional[Experience]:
        """Update existing experience"""
        experience = await self.get_experience_by_id(experience_id, user_id)

        if not experience:
            return None

        if payload.job_title is not None:
            experience.job_title = payload.job_title
        if payload.company_name is not None:
            experience.company_name = payload.company_name
        if payload.location is not None:
            experience.location = payload.location
        if payload.employment_type is not None:
            experience.employment_type = payload.employment_type
        if payload.start_date is not None:
            experience.start_date = payload.start_date
        if payload.end_date is not None:
            experience.end_date = payload.end_date
        if payload.is_current is not None:
            experience.is_current = payload.is_current
        if payload.description is not None:
            experience.description = payload.description
        if payload.achievements is not None:
            experience.achievements = payload.achievements
        if payload.technologies_used is not None:
            experience.technologies_used = payload.technologies_used
        if payload.display_order is not None:
            experience.display_order = payload.display_order
        if payload.is_active is not None:
            experience.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(experience)
        return experience

    async def delete_experience(self, experience_id: int, user_id: int) -> bool:
        """Delete experience by ID"""
        experience = await self.get_experience_by_id(experience_id, user_id)

        if not experience:
            return False

        await self.db.delete(experience)
        await self.db.commit()
        return True
