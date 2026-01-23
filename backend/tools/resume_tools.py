import base64
from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import sessionmanager
from models import (
    Education,
    Experience,
    PersonalInfo,
    Project,
    Summary,
    TechnicalSkill,
)
from services.cv_parser import CVParserService
from utils.logger import get_logger

logger = get_logger()


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Helper to parse YYYY-MM-DD string to date object."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


async def parse_and_save_cv(user_id: str, pdf_base64: str) -> Dict[str, Any]:
    """
    Parses a PDF resume (provided as base64 string) and saves the extracted data
    to the user's profile in the database.
    """
    try:
        # Decode PDF
        pdf_bytes = base64.b64decode(pdf_base64)

        # Parse
        parser_service = CVParserService()
        parsed_data = await parser_service.parse_cv(pdf_bytes)
        logger.info("Parsed Content from resume", extra={"Resume data": parsed_data})

        # Save to DB
        async for session in sessionmanager.get_session():
            await _save_parsed_data(session, UUID(user_id), parsed_data)

        return {
            "message": "CV parsed and saved successfully",
            "parsed_summary": parsed_data,
        }
    except Exception as e:
        logger.error("Error in parse_and_save_cv tool", extra={"error": str(e)})
        return {"error": str(e)}


async def _save_parsed_data(
    session: AsyncSession, user_id: UUID, parsed_data: Dict[str, Any]
):
    # Get user to ensure existence (optional check)

    # 1. Personal Info
    p_info = parsed_data.get("personal_info")
    if p_info:
        result = await session.execute(
            select(PersonalInfo).where(PersonalInfo.user_id == user_id)
        )
        personal_info = result.scalar_one_or_none()

        if personal_info:
            # Update existing
            if p_info.get("full_name"):
                personal_info.full_name = p_info.get("full_name")
            if p_info.get("email"):
                personal_info.email = p_info.get("email")
            if p_info.get("phone"):
                personal_info.phone = p_info.get("phone")
            if p_info.get("location"):
                personal_info.location = p_info.get("location")
            if p_info.get("linkedin_url"):
                personal_info.linkedin_url = p_info.get("linkedin_url")
            if p_info.get("github_url"):
                personal_info.github_url = p_info.get("github_url")
            if p_info.get("portfolio_url"):
                personal_info.portfolio_url = p_info.get("portfolio_url")
            if p_info.get("website_url"):
                personal_info.website_url = p_info.get("website_url")
            if p_info.get("professional_title"):
                personal_info.professional_title = p_info.get("professional_title")
        else:
            # Create new
            # We assume user exists, so we fetch their name if missing in CV
            # But for now, let's just use what's in CV or placeholders
            personal_info = PersonalInfo(
                user_id=user_id,
                full_name=p_info.get("full_name") or "User",  # Fallback
                email=p_info.get("email") or "unknown@example.com",
                phone=p_info.get("phone"),
                location=p_info.get("location"),
                linkedin_url=p_info.get("linkedin_url"),
                github_url=p_info.get("github_url"),
                portfolio_url=p_info.get("portfolio_url"),
                website_url=p_info.get("website_url"),
                professional_title=p_info.get("professional_title"),
            )
            session.add(personal_info)

    # 2. Education
    education_list = parsed_data.get("education", [])
    for edu in education_list:
        new_edu = Education(
            user_id=user_id,
            institution_name=edu.get("institution_name") or "Unknown Institution",
            degree=edu.get("degree") or "Unknown Degree",
            field_of_study=edu.get("field_of_study"),
            start_date=parse_date(edu.get("start_date")),
            end_date=parse_date(edu.get("end_date")),
            is_current=edu.get("is_current", False),
            grade=edu.get("grade"),
            location=edu.get("location"),
            description=edu.get("description"),
        )
        session.add(new_edu)

    # 3. Experiences
    experience_list = parsed_data.get("experiences", [])
    for exp in experience_list:
        new_exp = Experience(
            user_id=user_id,
            job_title=exp.get("job_title") or "Unknown Title",
            company_name=exp.get("company_name") or "Unknown Company",
            location=exp.get("location"),
            employment_type=exp.get("employment_type"),
            start_date=parse_date(exp.get("start_date")) or date.today(),
            end_date=parse_date(exp.get("end_date")),
            is_current=exp.get("is_current", False),
            description=exp.get("description"),
            achievements=exp.get("achievements"),
            technologies_used=exp.get("technologies_used"),
        )
        session.add(new_exp)

    # 4. Projects
    project_list = parsed_data.get("projects", [])
    for proj in project_list:
        new_proj = Project(
            user_id=user_id,
            project_name=proj.get("project_name") or "Unknown Project",
            description=proj.get("description") or "",
            highlights=proj.get("highlights"),
            project_url=proj.get("project_url"),
            github_url=proj.get("github_url"),
            start_date=parse_date(proj.get("start_date")),
            end_date=parse_date(proj.get("end_date")),
            technologies_used=proj.get("technologies_used"),
            is_featured=proj.get("is_featured", False),
        )
        session.add(new_proj)

    # 5. Skills
    skills_list = parsed_data.get("skills", [])
    if skills_list:
        new_skill_group = TechnicalSkill(
            user_id=user_id,
            category="Imported Skills",
            skills=skills_list,
            display_order=0,
        )
        session.add(new_skill_group)

    await session.commit()


async def get_user_profile_tool(user_id: str) -> Dict[str, Any]:
    """
    Retrieves the full profile of a user including all resume sections.
    """
    async for session in sessionmanager.get_session():
        # Cleanly fetching all related data
        # Ideally we'd use joinedload, but standard lazy loading might work if we are in session
        # Or we explicitly query each table.

        # NOTE: Since async, lazy loading relationships is harder (needs await).
        # We will do explicit queries to be safe and clear.

        uid = UUID(user_id)

        # Personal Info
        p_info_res = await session.execute(
            select(PersonalInfo).where(PersonalInfo.user_id == uid)
        )
        p_info = p_info_res.scalar_one_or_none()

        # Education
        edu_res = await session.execute(
            select(Education).where(Education.user_id == uid)
        )
        education = edu_res.scalars().all()

        # Experience
        exp_res = await session.execute(
            select(Experience).where(Experience.user_id == uid)
        )
        experiences = exp_res.scalars().all()

        # Projects
        proj_res = await session.execute(select(Project).where(Project.user_id == uid))
        projects = proj_res.scalars().all()

        # Skills
        skill_res = await session.execute(
            select(TechnicalSkill).where(TechnicalSkill.user_id == uid)
        )
        skills = skill_res.scalars().all()

        # Summary
        sum_res = await session.execute(select(Summary).where(Summary.user_id == uid))
        summary = sum_res.scalar_one_or_none()

        profile = {
            "personal_info": {
                "full_name": p_info.full_name,
                "email": p_info.email,
                "phone": p_info.phone,
                "linkedin_url": p_info.linkedin_url,
                "github_url": p_info.github_url,
                "portfolio_url": p_info.portfolio_url,
                "website_url": p_info.website_url,
                "professional_title": p_info.professional_title,
                "location": p_info.location,
            }
            if p_info
            else None,
            "education": [
                {
                    "institution_name": e.institution_name,
                    "degree": e.degree,
                    "start_date": e.start_date.isoformat() if e.start_date else None,
                    "end_date": e.end_date.isoformat() if e.end_date else None,
                    "description": e.description,
                }
                for e in education
            ],
            "experiences": [
                {
                    "company_name": e.company_name,
                    "job_title": e.job_title,
                    "start_date": e.start_date.isoformat() if e.start_date else None,
                    "end_date": e.end_date.isoformat() if e.end_date else None,
                    "description": e.description,
                    "achievements": e.achievements,
                    "technologies_used": e.technologies_used,
                }
                for e in experiences
            ],
            "projects": [
                {
                    "project_name": p.project_name,
                    "description": p.description,
                    "technologies_used": p.technologies_used,
                    "project_url": p.project_url,
                }
                for p in projects
            ],
            "skills": [{"category": s.category, "skills": s.skills} for s in skills],
            "summary": summary.summary_text if summary else None,
        }

        return profile
    return {}
