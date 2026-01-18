from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from models import (
    Education,
    Experience,
    PersonalInfo,
    Project,
    TechnicalSkill,
    User,
)
from services.cv_parser import CVParserService
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Helper to parse YYYY-MM-DD string to date object."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


@router.post("/upload_cv/")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    logger.info(
        "CV uploaded:", extra={"file_name": file.filename, "user_id": current_user.id}
    )

    try:
        contents = await file.read()
        parser_service = CVParserService()
        parsed_data = await parser_service.parse_cv(contents)
        logger.info("Parsed Content from resume", extra={"Resume data": parsed_data})
        #  Personal Info
        p_info_data = parsed_data.get("personal_info")
        if p_info_data:
            result = await db.execute(
                select(PersonalInfo).where(PersonalInfo.user_id == current_user.id)
            )
            personal_info = result.scalar_one_or_none()

            if personal_info:
                personal_info.full_name = (
                    p_info_data.get("full_name") or personal_info.full_name
                )
                personal_info.email = p_info_data.get("email") or personal_info.email
                personal_info.phone = p_info_data.get("phone") or personal_info.phone
                personal_info.location = (
                    p_info_data.get("location") or personal_info.location
                )
                personal_info.linkedin_url = (
                    p_info_data.get("linkedin_url") or personal_info.linkedin_url
                )
                personal_info.github_url = (
                    p_info_data.get("github_url") or personal_info.github_url
                )
                personal_info.portfolio_url = (
                    p_info_data.get("portfolio_url") or personal_info.portfolio_url
                )
                personal_info.website_url = (
                    p_info_data.get("website_url") or personal_info.website_url
                )
                personal_info.professional_title = (
                    p_info_data.get("professional_title")
                    or personal_info.professional_title
                )
            else:
                # Create new
                personal_info = PersonalInfo(
                    user_id=current_user.id,
                    full_name=p_info_data.get("full_name")
                    or f"{current_user.first_name} {current_user.last_name}",
                    email=p_info_data.get("email") or current_user.email,
                    phone=p_info_data.get("phone"),
                    location=p_info_data.get("location"),
                    linkedin_url=p_info_data.get("linkedin_url"),
                    github_url=p_info_data.get("github_url"),
                    portfolio_url=p_info_data.get("portfolio_url"),
                    website_url=p_info_data.get("website_url"),
                    professional_title=p_info_data.get("professional_title"),
                )
                db.add(personal_info)

        #  Education
        education_list = parsed_data.get("education", [])
        if education_list:
            for edu in education_list:
                new_edu = Education(
                    user_id=current_user.id,
                    institution_name=edu.get("institution_name")
                    or "Unknown Institution",
                    degree=edu.get("degree") or "Unknown Degree",
                    field_of_study=edu.get("field_of_study"),
                    start_date=parse_date(edu.get("start_date")),
                    end_date=parse_date(edu.get("end_date")),
                    is_current=edu.get("is_current", False),
                    grade=edu.get("grade"),
                    location=edu.get("location"),
                    description=edu.get("description"),
                )
                db.add(new_edu)

        # Experiences
        experience_list = parsed_data.get("experiences", [])
        if experience_list:
            for exp in experience_list:
                new_exp = Experience(
                    user_id=current_user.id,
                    job_title=exp.get("job_title") or "Unknown Title",
                    company_name=exp.get("company_name") or "Unknown Company",
                    location=exp.get("location"),
                    employment_type=exp.get("employment_type"),
                    start_date=parse_date(exp.get("start_date"))
                    or date.today(),  # valid start_date
                    end_date=parse_date(exp.get("end_date")),
                    is_current=exp.get("is_current", False),
                    description=exp.get("description"),
                    achievements=exp.get("achievements"),
                    technologies_used=exp.get("technologies_used"),
                )
                db.add(new_exp)

        #  Projects
        project_list = parsed_data.get("projects", [])
        if project_list:
            for proj in project_list:
                new_proj = Project(
                    user_id=current_user.id,
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
                db.add(new_proj)

        # Skills
        skills_list = parsed_data.get("skills", [])
        if skills_list:
            new_skill_group = TechnicalSkill(
                user_id=current_user.id,
                category="Imported Skills",
                skills=skills_list,
                display_order=0,
            )
            db.add(new_skill_group)

        await db.commit()

        return {
            "message": "CV parsed and saved successfully",
            "parsed_summary": {
                "personal_info": bool(p_info_data),
                "education_count": len(education_list),
                "experience_count": len(experience_list),
                "project_count": len(project_list),
                "skills_count": len(skills_list),
            },
        }

    except Exception as e:
        await db.rollback()
        logger.error(
            "Error processing CV upload:",
            extra={"error": str(e), "user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CV: {str(e)}",
        )
