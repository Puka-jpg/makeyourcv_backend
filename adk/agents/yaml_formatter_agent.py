"""
YAML Formatter Agent - Converts content JSON to valid RenderCV YAML.
"""

from google.adk.agents import Agent

from adk.callbacks.storage import persist_yaml_callback
from adk.mcp_config import build_tools_with_mcp
from adk.tools.state_tools import fetch_resume_data, store_tailored_resume_valid_yaml
from settings import settings

_local_tools = [fetch_resume_data, store_tailored_resume_valid_yaml]

yaml_formatter_agent = Agent(
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
    2. Convert JSON to RenderCV YAML format.
    3. Call `validate_cv(yaml_content=...)`. 
       - This tool is an MCP tool.
    4. IF valid:
       - Call `store_tailored_resume_valid_yaml(yaml_content=...)`.
       - Respond: "YAML is valid and stored."
    5. IF invalid (error returned):
       - Fix the YAML based on the error.
       - Retry validation (Call `validate_cv` again).
       - Repeat until valid or max steps reached.
    """,
)
