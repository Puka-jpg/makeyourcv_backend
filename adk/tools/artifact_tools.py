"""
ADK Artifact Management Tools.
"""

import base64
import os
import uuid
from typing import Any, Dict, Optional

from google.adk.tools import ToolContext
from google.genai import types

from utils.logger import get_logger

logger = get_logger()

OUTPUT_DIR = "generated_resumes"


async def save_pdf_artifact(
    base64_blob: str,
    tool_context: ToolContext,
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Saves a base64-encoded PDF to the local 'generated_resumes' directory
    AND as an ADK artifact.
    """
    try:
        if "," in base64_blob[:100]:
            base64_blob = base64_blob.split(",", 1)[1]

        pdf_bytes = base64.b64decode(base64_blob)
        if not filename:
            filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"

        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        await tool_context.save_artifact(filename=filename, artifact=pdf_part)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_path = os.path.join(OUTPUT_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        download_url = f"/generated_resumes/{filename}"
        tool_context.state["latest_resume_url"] = download_url
        tool_context.state["latest_resume_filename"] = filename

        logger.info(
            "PDF saved successfully",
            extra={
                "path": file_path,
                "url": download_url,
                "size": len(pdf_bytes),
            },
        )

        return {
            "status": "success",
            "message": "PDF saved to artifacts and disk.",
            "filename": filename,
            "download_url": download_url,
            "size_bytes": len(pdf_bytes),
        }

    except Exception as e:
        logger.exception("Failed to save PDF artifact")
        return {"status": "error", "message": str(e)}


async def convert_yaml_to_rendercv_input(
    yaml_content: str, tool_context: ToolContext
) -> Dict[str, str]:
    """
    Validates and stores YAML content for render_cv tool.
    """
    if not yaml_content or not yaml_content.strip():
        raise ValueError("YAML content cannot be empty")

    tool_context.state["_last_yaml_input"] = yaml_content

    return {
        "status": "ready",
        "message": f"YAML ({len(yaml_content)} chars) ready for rendering.",
    }
