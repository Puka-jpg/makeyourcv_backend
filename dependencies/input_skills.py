from models import Skills
from schemas.input_skills import SkillCreateSchema


class InputSkills:
    def __init__(self, db):
        self.db = db

    async def input_skill(self, payload: SkillCreateSchema):
        skill = Skills(
            skill_name=payload.skill_name, skill_description=payload.skill_description
        )
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill
