from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Resume
from utils.logger import get_logger

logger = get_logger()


class ResumeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_resume(self, resume_id: UUID) -> Optional[Resume]:
        result = await self.session.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        return result.scalars().first()

    async def create_resume(self, user_id: UUID) -> Resume:
        resume = Resume(user_id=user_id, job_description="")
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def update_raw_text(self, resume_id: UUID, text: str):
        stmt = (
            update(Resume)
            .where(Resume.id == resume_id)
            .values(raw_resume_text=text, status="parsed")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info(
            "Updated raw_resume_text",
            extra={"resume_id": str(resume_id), "text_len": len(text)},
        )

    async def update_job_description(self, resume_id: UUID, text: str):
        stmt = update(Resume).where(Resume.id == resume_id).values(job_description=text)
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info("Updated job_description", extra={"resume_id": str(resume_id)})

    async def update_tailored_content(self, resume_id: UUID, content_json: str):
        stmt = (
            update(Resume)
            .where(Resume.id == resume_id)
            .values(tailored_content_json=content_json, status="tailored_content")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info("Updated tailored_content", extra={"resume_id": str(resume_id)})

    async def update_tailored_yaml(self, resume_id: UUID, yaml_content: str):
        stmt = (
            update(Resume)
            .where(Resume.id == resume_id)
            .values(tailored_resume_yaml=yaml_content, status="yaml_ready")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        logger.info("Updated tailored_yaml", extra={"resume_id": str(resume_id)})

    async def update_pdf_path(self, resume_id: UUID, file_path: str):
        stmt = (
            update(Resume)
            .where(Resume.id == resume_id)
            .values(file_path=file_path, status="completed")
        )
        await self.session.execute(stmt)
        await self.session.commit()
