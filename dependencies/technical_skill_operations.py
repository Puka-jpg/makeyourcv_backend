from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TechnicalSkill
from schemas.user_input_schemas.technical_skill_schemas import (
    TechnicalSkillCreateSchema,
    TechnicalSkillUpdateSchema,
)


class TechnicalSkillOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_technical_skill(
        self, payload: TechnicalSkillCreateSchema
    ) -> TechnicalSkill:
        """Create technical skill in the database"""
        technical_skill = TechnicalSkill(
            user_id=payload.user_id,
            category=payload.category,
            skills=payload.skills,
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(technical_skill)
        await self.db.commit()
        await self.db.refresh(technical_skill)
        return technical_skill

    async def get_all_technical_skills(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[TechnicalSkill]:
        """Retrieve all technical skills for a user"""
        query = (
            select(TechnicalSkill)
            .where(TechnicalSkill.user_id == user_id)
            .order_by(TechnicalSkill.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        skills = result.scalars().all()
        return list(skills)

    async def get_technical_skill_by_id(
        self, skill_id: int, user_id: int
    ) -> Optional[TechnicalSkill]:
        """Retrieve single technical skill by ID"""
        query = select(TechnicalSkill).where(
            TechnicalSkill.id == skill_id, TechnicalSkill.user_id == user_id
        )
        result = await self.db.execute(query)
        skill = result.scalar_one_or_none()
        return skill

    async def update_technical_skill(
        self, skill_id: int, user_id: int, payload: TechnicalSkillUpdateSchema
    ) -> Optional[TechnicalSkill]:
        """Update existing technical skill"""
        skill = await self.get_technical_skill_by_id(skill_id, user_id)

        if not skill:
            return None

        if payload.category is not None:
            skill.category = payload.category
        if payload.skills is not None:
            skill.skills = payload.skills
        if payload.display_order is not None:
            skill.display_order = payload.display_order
        if payload.is_active is not None:
            skill.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def delete_technical_skill(self, skill_id: int, user_id: int) -> bool:
        """Delete technical skill by ID"""
        skill = await self.get_technical_skill_by_id(skill_id, user_id)

        if not skill:
            return False

        await self.db.delete(skill)
        await self.db.commit()
        return True
