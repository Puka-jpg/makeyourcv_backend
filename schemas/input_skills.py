from pydantic import BaseModel


class SkillCreateSchema(BaseModel):
    skill_name: str
    skill_description: str
