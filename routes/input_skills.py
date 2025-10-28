from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.input_skills import InputSkills
from schemas.input_skills import SkillCreateSchema

router = APIRouter()


@router.post("/")
async def input_skills(
    skills_payload: SkillCreateSchema, db: AsyncSession = Depends(get_db)
):
    res = InputSkills(db)
    skill = await res.input_skill(skills_payload)
    return skill
