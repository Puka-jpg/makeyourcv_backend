"""
State management tools for ADK agents.

These tools allow agents to read and write to session state.
Refactored for DB-centric architecture:
- Stores `resume_id` to link to DB.
- Stores availability flags (e.g., `resume_uploaded`).
- Includes internal "store" tools that place data in state for callbacks to persist.
"""

import uuid
from typing import Any, Dict, Optional

from google.adk.tools import ToolContext

from adk.services.resume_service import ResumeService
from db import sessionmanager
from utils.logger import get_logger

logger = get_logger()


async def get_current_state(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Returns the current session state.
    """
    state = tool_context.state
    result: Dict[str, Any] = {}

    keys_to_check = [
        "resume_id",
        "resume_uploaded", 
        "job_description_provided", 
        "tailored_content_ready", 
        "user_id",
        "current_step",
    ]

    for key in keys_to_check:
        val = state.get(key)
        if val is not None:
            result[key] = val

    logger.info("Current state keys present", extra={"keys": list(result.keys())})
    return result


async def init_resume_session(
    user_id_str: Optional[str] = None,
    tool_context: ToolContext = None,  # type: ignore
) -> Dict[str, str]:
    """
    Initializes a new resume session in the DB.

    CRITICAL: You should usually call this WITHOUT arguments, as it automatically detects the current user.
    Example: `init_resume_session()`

    Args:
        user_id_str: Optional. Only used if you need to override the current user.
        tool_context: Injected automatically.
    """
    try:
        if tool_context is None:
            return {"status": "error", "message": "ToolContext was not injected"}

        user_id_val = tool_context.state.get("user_id")
        if not user_id_val:
            user_id_val = user_id_str

        if not user_id_val:
            return {
                "status": "error",
                "message": "User ID missing. Cannot initialize session.",
            }

        try:
            user_id = uuid.UUID(str(user_id_val))
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid User ID format: {user_id_val}",
            }

        if not sessionmanager.session_factory:
            raise RuntimeError("Database not initialized")

        async with sessionmanager.session_factory() as session:
            service = ResumeService(session)
            resume = await service.create_resume(user_id=user_id)
            resume_id = str(resume.id)

            if tool_context and hasattr(tool_context, "session_id"):
                from google.adk.sessions.database_session_service import StorageSession
                from sqlalchemy import select


                stmt = select(StorageSession).where(
                    StorageSession.id == tool_context.session_id
                )
                result = await session.execute(stmt)
                storage_session = result.scalars().first()

                if storage_session:
                    new_state = (
                        storage_session.state.copy() if storage_session.state else {}
                    )
                    new_state["resume_id"] = resume_id
                    new_state["resume_uploaded"] = False
                    new_state["job_description_provided"] = False

                    storage_session.state = new_state  # type: ignore
                    await session.commit()
                    logger.info(
                        "Force-persisted resume_id to session",
                        extra={
                            "resume_id": resume_id,
                            "session_id": str(tool_context.session_id),
                        },
                    )

        tool_context.state["resume_id"] = resume_id
        tool_context.state["resume_uploaded"] = False
        tool_context.state["job_description_provided"] = False

        return {
            "status": "success",
            "message": f"Initialized resume session {resume_id}",
            "resume_id": resume_id,
        }
    except Exception as e:
        logger.exception("Failed to init resume session")
        return {"status": "error", "message": str(e)}


async def fetch_resume_data(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Fetches the actual text data from DB for agents that need it.
    Use this sparingly to avoid context overload.

    Returns:
        Dict containing 'raw_resume_text' and 'job_description' if available.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return {"status": "error", "message": "No resume_id in state"}

    if not sessionmanager.session_factory:
        return {"status": "error", "message": "Database not initialized"}

    async with sessionmanager.session_factory() as session:
        service = ResumeService(session)
        resume = await service.get_resume(uuid.UUID(resume_id_str))

        if not resume:
            return {"status": "error", "message": "Resume record not found"}

        def safe_str(val: Any) -> Optional[str]:
            return str(val) if val is not None else None

        return {
            "status": "success",
            "raw_resume_text": safe_str(resume.raw_resume_text),
            "job_description": safe_str(resume.job_description),
            "tailored_content_json": safe_str(resume.tailored_content_json),
            "tailored_resume_valid_yaml": safe_str(resume.tailored_resume_yaml),
        }


# --- Internal Tools for Agents (Data Passing to Callbacks) ---


async def store_job_description(job_description: str, tool_context: ToolContext) -> str:
    """
    Stores the raw job description text in the state (temporarily).
    The 'persist_job_description' callback will move this to the DB.
    """
    tool_context.state["raw_job_description"] = job_description
    return "Job description stored in temporary state."


async def store_tailored_content_json(
    content_json: str, tool_context: ToolContext
) -> str:
    """
    Stores the tailored content JSON in the state (temporarily).
    The 'persist_tailored_content' callback will move this to the DB.
    """
    tool_context.state["tailored_content_json"] = content_json
    return "Tailored content JSON stored in temporary state."


async def store_tailored_resume_valid_yaml(
    yaml_content: str, tool_context: ToolContext
) -> str:
    """
    Stores the validated YAML in the state (temporarily).
    The 'persist_yaml' callback will move this to the DB.
    """
    tool_context.state["tailored_resume_valid_yaml"] = yaml_content
    return "Tailored YAML stored in temporary state."


async def store_resume_text(resume_text: str, tool_context: ToolContext) -> str:
    """
    Stores the raw resume text in the state (temporarily).
    """
    tool_context.state["raw_resume_text"] = resume_text
    return "Resume text stored in temporary state."
