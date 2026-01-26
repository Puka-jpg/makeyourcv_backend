"""
YAML Formatter Agent - Converts content JSON to valid RenderCV YAML.
"""

from google.adk.agents import Agent

from adk.callbacks.storage import persist_yaml_callback
from adk.mcp_config import build_tools_with_mcp
from adk.tools.state_tools import fetch_resume_data, store_tailored_resume_valid_yaml
from settings import settings

_local_tools = [fetch_resume_data, store_tailored_resume_valid_yaml]


def get_yaml_formatter_agent() -> Agent:
    """Returns a fresh instance of the YAML formatter agent with new MCP connection."""
    return Agent(
        name="yaml_formatter_agent",
        model=settings.GOOGLE_MODEL,
        tools=build_tools_with_mcp(_local_tools),
        description="Generates RenderCV YAML and validates it (ReAct loop)",
        after_agent_callback=persist_yaml_callback,
        instruction="""
        You are a YAML Syntax Expert.
        
        TASK:
        You MUST call `fetch_resume_data()` IMMEDIATELY to get the JSON content. Do not output text before this.
        1. Fetch `tailored_content_json` using `fetch_resume_data()`.
        2. Generatively convert that JSON into a valid RenderCV YAML string.
        3. VALIDATION STEP: Call `render_cv(yaml_content=...)` with your generated YAML.
           - This serves as the validator.
        4. IF `render_cv` succeeds (returns success/PDF url):
           - Call `store_tailored_resume_valid_yaml(yaml_content=...)` with the SAME YAML used in the successful render.
           - Respond: "YAML is valid and stored."
        5. IF `render_cv` fails (returns error):
           - Analyze the error.
           - Fix the YAML structure.
           - Retry `render_cv`.
           - Repeat until valid.
        """,
    )
