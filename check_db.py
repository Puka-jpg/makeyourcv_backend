
import asyncio
from sqlalchemy import select
from db import sessionmanager
from models import Resume
from utils.logger import get_logger

logger = get_logger()

async def check_db():
    sessionmanager.init_db()
    async with sessionmanager.session_factory() as session:
        result = await session.execute(select(Resume))
        resumes = result.scalars().all()
        
        print(f"Found {len(resumes)} resumes.")
        for r in resumes:
            print(f"Resume ID: {r.id}")
            print(f"  User ID: {r.user_id}")
            print(f"  Raw Text Len: {len(r.raw_resume_text) if r.raw_resume_text else 0}")
            print(f"  JD Len: {len(r.job_description) if r.job_description else 0}")
            print(f"  Tailored Content JSON Len: {len(r.tailored_content_json) if r.tailored_content_json else 0}")
            print(f"  Tailored YAML Len: {len(r.tailored_resume_yaml) if r.tailored_resume_yaml else 0}")
            
if __name__ == "__main__":
    asyncio.run(check_db())
