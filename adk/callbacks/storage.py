from typing import Any
from uuid import UUID

from adk.services.resume_service import ResumeService
from db import sessionmanager
from utils.logger import get_logger

logger = get_logger()


async def persist_parsed_resume(callback_context: Any) -> None:
    """
    After parser_agent, save extracted text to DB and set flag in state.
    """

    state = callback_context.state
    resume_id_str = state.get("resume_id")

    if not resume_id_str:
        logger.error("No resume_id in state")
        return

    raw_text = state.get("raw_resume_text")

    if raw_text:
        if not sessionmanager.session_factory:
            logger.error("DB not initialized")
            return

        async with sessionmanager.session_factory() as session:
            service = ResumeService(session)
            await service.update_raw_text(UUID(resume_id_str), raw_text)

        try:
            del state["raw_resume_text"]
        except (KeyError, AttributeError):
            pass

        state["resume_uploaded"] = True
        logger.info("Persisted raw resume text to DB.")


async def persist_job_description_callback(callback_context: Any) -> None:
    state = callback_context.state
    resume_id_str = state.get("resume_id")

    if not resume_id_str:
        return

    jd_text = state.get("raw_job_description")

    if jd_text:
        if not sessionmanager.session_factory:
            logger.error("DB not initialized")
            return

        async with sessionmanager.session_factory() as session:
            service = ResumeService(session)
            await service.update_job_description(UUID(resume_id_str), jd_text)

        try:
            del state["raw_job_description"]
        except (KeyError, AttributeError):
            pass

        state["job_description_provided"] = True


async def persist_tailored_content_callback(callback_context: Any) -> None:
    state = callback_context.state
    resume_id_str = state.get("resume_id")
    if not resume_id_str:
        return

    content = state.get("tailored_content_json")
    if content:
        if not sessionmanager.session_factory:
            logger.error("DB not initialized")
            return

        async with sessionmanager.session_factory() as session:
            service = ResumeService(session)
            await service.update_tailored_content(UUID(resume_id_str), content)

        try:
            del state["tailored_content_json"]
        except (KeyError, AttributeError):
            pass

        state["tailored_content_ready"] = True


async def persist_yaml_callback(callback_context: Any) -> None:
    state = callback_context.state
    resume_id_str = state.get("resume_id")
    if not resume_id_str:
        return

    yaml_content = state.get("tailored_resume_valid_yaml")
    if yaml_content:
        if not sessionmanager.session_factory:
            logger.error("DB not initialized")
            return

        async with sessionmanager.session_factory() as session:
            service = ResumeService(session)
            await service.update_tailored_yaml(UUID(resume_id_str), yaml_content)

        try:
            del state["tailored_resume_valid_yaml"]
        except (KeyError, AttributeError):
            pass

        state["yaml_ready"] = True
