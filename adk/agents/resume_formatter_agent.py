"""
Resume Formatter Agent - Renders PDF from stored valid YAML.
"""

from google.adk.agents import Agent

from adk.mcp_config import build_tools_with_mcp
from adk.tools.artifact_tools import save_pdf_artifact
from adk.tools.state_tools import fetch_resume_data
from settings import settings

_local_tools = [fetch_resume_data, save_pdf_artifact]


def get_resume_formatter_agent() -> Agent:
    return Agent(
        name="resume_formatter_agent",
        model=settings.GOOGLE_MODEL,
        description="Formats resume data into PDF using RenderCV",
        tools=build_tools_with_mcp(_local_tools),
        instruction="""
        You are the Resume Formatting Specialist.
        Your sole responsibility is to convert VALIDATED YAML (from DB) into a PDF.

        WORKFLOW:
        1. Call `fetch_resume_data()` to retrieve `tailored_resume_valid_yaml` (mapped from 'tailored_resume_yaml' column).
           - Note: The tool returns `raw_resume_text`, `job_description`, and `tailored_content_json`. 
           - Wait, `fetch_resume_data` in state_tools needs to return `tailored_resume_yaml` too.
           - Assuming it does or checks will fail.
        
        2. Call `render_cv(yaml_content=...)` (MCP Tool).
           - Pass the YAML string retrieved from DB.
           - IF success: Proceed.
           - IF failure: Retry once. If it fails again, report the specific error.
        
        3. Call `save_pdf_artifact(base64_blob=...)` with the result.
        
        4. Respond: "Resume generated successfully. You can download it here: [download_url] (or check the `generated_resumes` folder)."
           - Replace `[download_url]` with the actual URL returned by `save_pdf_artifact`.
        """,
    )
