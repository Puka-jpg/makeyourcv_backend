"""
Job Analysis Agent - Summarizes job description.
"""

from google.adk.agents import Agent

from adk.callbacks.storage import persist_job_description_callback
from adk.tools.state_tools import store_job_description
from settings import settings

_local_tools = [store_job_description]

job_analysis_agent = Agent(
    name="job_analysis_agent",
    model=settings.GOOGLE_MODEL,
    tools=_local_tools,
    after_agent_callback=persist_job_description_callback,
    description="Analyzes job descriptions and stores raw info",
    instruction="""
    You are an expert job description analyzer.
    
    TASK:
    1. Analyze the job description provided by the user.
    2. Call `store_job_description(job_description=...)` with the text.
    3. Return: "Job description analyzed and stored."
    
    The callback will handle DB persistence.
    """,
)
