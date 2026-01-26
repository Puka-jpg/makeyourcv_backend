from google.adk.agents import Agent

from adk.agents.content_tailor_agent import get_content_tailor_agent
from adk.agents.job_analysis_agent import get_job_analysis_agent
from adk.agents.parser_agent import get_parser_agent
from adk.agents.resume_formatter_agent import get_resume_formatter_agent
from adk.agents.yaml_formatter_agent import get_yaml_formatter_agent
from adk.tools.state_tools import get_current_state, init_resume_session
from settings import settings

# Get fresh instance of dynamic agents
parser = get_parser_agent()
job_analysis = get_job_analysis_agent()
content_tailor = get_content_tailor_agent()
yaml_formatter = get_yaml_formatter_agent()
resume_formatter = get_resume_formatter_agent()

_sub_agents = [
    parser,
    job_analysis,
    content_tailor,
    yaml_formatter,
    resume_formatter,
]

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=settings.GOOGLE_MODEL,
    description="Orchestrates the resume building process dynamically",
    tools=[init_resume_session, get_current_state],
    sub_agents=_sub_agents,
    instruction="""
        You are the Resume Builder Orchestrator.
        
        YOUR GOAL: Guide the user strictly through: Upload -> Job Desc -> Tailor -> Format -> Render.
        
        ### STATE & ROUTING (CHECK `get_current_state` EVERY TURN)
        
        1. **Initialization**:
           - IF `resume_id` is MISSING: Call `init_resume_session()`.
           
        2. **Resume Parsing**:
           - IF `resume_id` exists BUT `resume_uploaded` is False:
             - IF `resume_file_path` is in state -> Transfer to `parser_agent`.
             - ELSE -> Ask user to upload a resume.

        3. **Job Description**:
           - IF `job_description_provided` is False:
             - Transfer to `job_analysis_agent` (handles both text input and analysis).
        
        4. **Tailoring**:
           - IF `resume_uploaded` AND `job_description_provided` are True:
           - AND `tailored_content_ready` is False:
             - Ask confirmation, then transfer to `content_tailor_agent`.

        5. **Formatting (YAML)**:
           - IF `tailored_content_ready` is True AND `yaml_ready` is NOT True:
             - Transfer to `yaml_formatter_agent`. This agent generates the YAML needed for PDF.

        6. **Rendering (PDF)**:
           - IF `yaml_ready` is True AND `rendering_complete` is NOT True:
             - Transfer to `resume_formatter_agent`.
             
        CRITICAL:
        - Do not skip steps.
        - Do not guess state. Call `get_current_state()` if unsure.
        """,
)


# Expose a static instance for CLI tools (like `adk web`)
root_agent = orchestrator_agent
