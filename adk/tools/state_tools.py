"""
State management tools for ADK agents.

These tools allow agents to read and write to session state.
Refactored for DB-centric architecture:
- Stores `resume_id` to link to DB.
- Stores availability flags (e.g., `resume_uploaded`).
- Writes large data directly to DB.
"""

import uuid
from typing import Any, Dict, Optional

from google.adk.tools import ToolContext

from adk.services.resume_service import ResumeService
from db import sessionmanager
from utils.logger import get_logger

# Helper for Lazy Init
def ensure_db_initialized():
    if not sessionmanager.session_factory:
        get_logger().info("Lazy initializing DB for tool execution")
        sessionmanager.init_db()


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
        "yaml_ready",
        "rendering_complete",
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
    """
    try:
        ensure_db_initialized()


        if tool_context is None:
            return {"status": "error", "message": "ToolContext was not injected"}

        user_id_val = tool_context.state.get("user_id")
        if not user_id_val:
            user_id_val = user_id_str

        if not user_id_val:
            # Fallback for adk web / dev mode: Find or create a default dev user
            logger.warning("User ID missing. Attempting to use default dev user for 'adk web' compatibility.")
            
            if not sessionmanager.session_factory:
                 raise RuntimeError("Database not initialized")
                 
            async with sessionmanager.session_factory() as session:
                from sqlalchemy import select
                from models import User
                
                # Check for existing user
                stmt = select(User).limit(1)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user_id = user.id
                    user_id_val = str(user_id)
                    logger.info(f"Using existing user as fallback: {user_id}")
                else:
                    # Create default dev user
                    new_user_id = uuid.uuid4()
                    user = User(
                        id=new_user_id,
                        first_name="Dev",
                        last_name="User",
                        email="dev@example.com",
                        hashed_password="dev_password_placeholder"
                    )
                    session.add(user)
                    await session.commit()
                    user_id = new_user_id
                    user_id_val = str(new_user_id)
                    logger.info(f"Created new dev user: {user_id}")
            
            # Update state with the discovered/created user_id
            tool_context.state["user_id"] = user_id_val

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
            # Create new resume record
            resume = await service.create_resume(user_id=user_id)
            resume_id = str(resume.id)

            # Initial update for User ID if needed (though create_resume does it)
            # No need to touch StorageSession table directly. ADK handles state persistence.

        # Update State (Flags)
        tool_context.state["resume_id"] = resume_id
        tool_context.state["resume_uploaded"] = False
        tool_context.state["job_description_provided"] = False
        tool_context.state["tailored_content_ready"] = False
        tool_context.state["yaml_ready"] = False
        tool_context.state["rendering_complete"] = False

        # If resume file was uploaded in route, we might want to check here?
        # But the route sets 'resume_uploaded' to True if file exists.
        # Wait, if we init session, we might overwrite what route did?
        # Route logic: injects 'resume_file_path'.
        # If 'resume_file_path' is in state, we shouldn't reset resume_uploaded to False?

        if tool_context.state.get("resume_file_path"):
            tool_context.state["resume_uploaded"] = True

        return {
            "status": "success",
            "message": f"Initialized resume session {resume_id}",
            "resume_id": resume_id,
        }
    except Exception as e:
        logger.exception("Failed to init resume session")
        if tool_context and hasattr(tool_context, "state"):
            tool_context.state["error_message"] = f"Init failed: {str(e)}"
        return {"status": "error", "message": str(e)}


async def fetch_resume_data(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Fetches the actual text data from DB for agents that need it.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return {"status": "error", "message": "No resume_id in state"}

    ensure_db_initialized()
        
    if not sessionmanager.session_factory:
        return {"status": "error", "message": "Database not initialized"}

    # Mypy assertion
    assert sessionmanager.session_factory is not None

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


# --- Internal Tools for Agents (Writing directly to DB) ---


async def store_job_description(job_description: str, tool_context: ToolContext) -> str:
    """
    Stores the job description text in the DB.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return "Error: No resume_id in state."

    ensure_db_initialized()
    assert sessionmanager.session_factory is not None
    async with sessionmanager.session_factory() as session:
        service = ResumeService(session)
        await service.update_job_description(uuid.UUID(resume_id_str), job_description)

    tool_context.state["job_description_provided"] = True
    return "Job description stored in DB."


async def store_tailored_content_json(
    content_json: str, tool_context: ToolContext
) -> str:
    """
    Stores the tailored content JSON in the DB.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return "Error: No resume_id in state."

    ensure_db_initialized()
    assert sessionmanager.session_factory is not None
    async with sessionmanager.session_factory() as session:
        service = ResumeService(session)
        await service.update_tailored_content(uuid.UUID(resume_id_str), content_json)

    tool_context.state["tailored_content_ready"] = True
    return "Tailored content JSON stored in DB."


async def store_tailored_resume_valid_yaml(
    yaml_content: str, tool_context: ToolContext
) -> str:
    """
    Stores the validated YAML in the DB.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return "Error: No resume_id in state."

    ensure_db_initialized()
    assert sessionmanager.session_factory is not None
    async with sessionmanager.session_factory() as session:
        service = ResumeService(session)
        await service.update_tailored_yaml(uuid.UUID(resume_id_str), yaml_content)

    tool_context.state["yaml_ready"] = True
    return "Tailored YAML stored in DB."


async def store_resume_text(resume_text: str, tool_context: ToolContext) -> str:
    """
    Stores the raw resume text in the DB.
    """
    resume_id_str = tool_context.state.get("resume_id")
    if not resume_id_str:
        return "Error: No resume_id in state."

    ensure_db_initialized()
    assert sessionmanager.session_factory is not None
    async with sessionmanager.session_factory() as session:
        service = ResumeService(session)
        await service.update_raw_text(uuid.UUID(resume_id_str), resume_text)

    tool_context.state["resume_uploaded"] = True
    return "Resume text stored in DB."
