import base64
from typing import Any

from google.adk.tools import ToolContext

from services.cv_parser import CVParserService
from utils.logger import get_logger

logger = get_logger()


async def extract_resume_text_tool(tool_context: ToolContext) -> str:
    """
    Extracts raw text from resume bytes stored in the session state.
    """
    service = CVParserService()

    resume_b64: Any = tool_context.state.get("resume_bytes_b64")
    if not resume_b64 or not isinstance(resume_b64, str):
        logger.error("Resume bytes missing or invalid in state")
        raise ValueError("Resume data not found in session state.")

    try:
        content = base64.b64decode(resume_b64)
        text = service.extract_text_from_pdf(content)

        tool_context.state["raw_resume_text"] = text
        return text

    except Exception as e:
        logger.exception("Failed to decode or parse resume bytes")
        raise RuntimeError(f"Resume parsing failed: {str(e)}") from e
