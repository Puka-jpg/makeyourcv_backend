from google.adk.tools import ToolContext

from services.cv_parser import CVParserService
from utils.logger import get_logger

logger = get_logger()


async def extract_resume_text_tool(tool_context: ToolContext) -> str:
    """
    Extracts raw text from resume file on disk and stores it in the DB.
    """
    resume_path = tool_context.state.get("resume_file_path")
    resume_id_str = tool_context.state.get("resume_id")

    if not resume_path:
        logger.error("Resume file path missing in state")
        raise ValueError("No resume file found. Please upload a resume first.")

    if not resume_id_str:
        logger.error("Resume ID missing in state")
        raise ValueError("Session not initialized correctly (missing resume_id).")

    service = CVParserService()

    try:
        import uuid

        from adk.services.resume_service import ResumeService
        from db import sessionmanager

        with open(resume_path, "rb") as f:
            content = f.read()

        text = service.extract_text_from_pdf(content)

        # Persist to DB directly
        if not sessionmanager.session_factory:
            raise RuntimeError("Database not initialized")

        assert sessionmanager.session_factory is not None

        async with sessionmanager.session_factory() as session:
            resume_service = ResumeService(session)
            await resume_service.update_raw_text(uuid.UUID(resume_id_str), text)

        tool_context.state["resume_uploaded"] = True

        return "Resume text extracted and stored in database successfully."

    except Exception as e:
        logger.exception("Failed to parse resume file")
        raise RuntimeError(f"Resume parsing failed: {str(e)}") from e
