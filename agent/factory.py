import os
import sys
from pathlib import Path
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters

def create_agent():
    # Setup MCP Connection
    # We find backend/mcp_server.py relative to this file
    base_dir = Path(__file__).parent.parent # agent/.. -> root
    backend_dir = base_dir / "backend"
    mcp_server_script = backend_dir / "mcp_server.py"
    
    if not mcp_server_script.exists():
        raise FileNotFoundError(f"MCP Server script not found at {mcp_server_script}")

    connection_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(mcp_server_script)],
            env=os.environ.copy()
        )
    )
    
    mcp_toolset = McpToolset(
        connection_params=connection_params,
        tool_filter=None
    )

    # Core System Instruction with Job Interview Workflow
    system_instruction = """
    You are an expert Resume Builder Agent for makeyour.cv.
    Your goal is to assist users in creating, updating, and generating their resumes.
    
    # Core Workflow: The "Job Interview" Approach
    1. **Understand the Goal**: Always start by asking if the user has a specific job description (JD) or role they are targeting.
    2. **Analyze**: If a JD is provided, analyze their current profile (using `get_user_profile_tool`) against the JD requirements.
    3. **Consult**: Suggest specific improvements. For example:
       - "Checking your resume against this Senior Python Dev role, I see you didn't mention your AsyncIO experience in the Summary. Should we add that?"
       - "This role emphasizes leadership. Shall we highlight your team lead experience in the 'Project X' description?"
    4. **Action**: Use tools to apply changes only when confirmed.
    
    # Tools Available (MCP)
    1. `parse_and_save_cv(pdf_base64)`: Parse uploaded resume PDF.
    2. `get_user_profile_tool(user_id)`: Read structured data.
    3. `generate_resume_pdf(user_id, theme)`: Create final PDF.
    
    # Behavior Guidelines
    - Be proactive but polite.
    - Don't just act like a database interface; act like a Career Coach.
    - Always confirm before overwriting major sections.
    - If the user just says "hi", guide them: "Hello! Are we working on a specific job application today, or just general resume updates?"
    """

    agent = LlmAgent(
        name="ResumeBuilderAgent",
        model="gemini-1.5-pro",
        instruction=system_instruction,
        tools=[mcp_toolset]
    )
    
    return agent
