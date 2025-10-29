from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Skills
from schemas.skill_schemas import SkillCreateSchema, SkillUpdateSchema


class SkillOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_skill(self, payload: SkillCreateSchema) -> Skills:
        """Create a new skill in the database"""
        skill = Skills(
            skill_name=payload.skill_name, skill_description=payload.skill_description
        )
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def get_all_skills(self, skip: int = 0, limit: int = 100) -> List[Skills]:
        """Retrieve all skills with pagination"""
        query = select(Skills).offset(skip).limit(limit)
        result = await self.db.execute(query)
        skills = result.scalars().all()
        return list(skills)

    async def get_skill_by_id(self, skill_id: int) -> Optional[Skills]:
        """Retrieve a single skill by its ID"""
        query = select(Skills).where(Skills.id == skill_id)
        result = await self.db.execute(query)
        skill = result.scalar_one_or_none()
        return skill

    async def update_skill(
        self, skill_id: int, payload: SkillUpdateSchema
    ) -> Optional[Skills]:
        """Update an existing skill"""
        skill = await self.get_skill_by_id(skill_id)

        if not skill:
            return None

        # Update only the fields that are provided
        if payload.skill_name is not None:
            skill.skill_name = payload.skill_name

        if payload.skill_description is not None:
            skill.skill_description = payload.skill_description

        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def delete_skill(self, skill_id: int) -> bool:
        """Delete a skill by its ID"""
        skill = await self.get_skill_by_id(skill_id)

        if not skill:
            return False

        await self.db.delete(skill)
        await self.db.commit()
        return True

    async def skill_exists(self, skill_name: str) -> bool:
        """Check if a skill with the given name already exists"""
        query = select(Skills).where(Skills.skill_name == skill_name)
        result = await self.db.execute(query)
        skill = result.scalar_one_or_none()
        return skill is not None

    async def get_skills_count(self) -> int:
        """Get total count of skills in database"""
        query = select(Skills)
        result = await self.db.execute(query)
        skills = result.scalars().all()
        return len(skills)
