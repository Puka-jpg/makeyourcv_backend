"""
Parser Agent - Extracts text from Resume PDF.
"""

from google.adk.agents import Agent

from adk.tools.parser_tool import extract_resume_text_tool
from settings import settings


def get_parser_agent() -> Agent:
    return Agent(
        name="parser_agent",
        model=settings.GOOGLE_MODEL,
        tools=[extract_resume_text_tool],
        # Persistence handled by tool directly
        description="Extracts raw text from a PDF resume file",
        instruction="""
        You are the Resume Parser.
        
        TASK:
        1. Receive the resume file (PDF) from the context.
        2. Call `extract_resume_text_tool` to get the raw text.
        3. Return ONLY: "Resume text extracted and stored. Proceed to job description."
        
        DO NOT output the raw extracted text in the chat.
        DO NOT store anything in state manually. The system handles persistence.
        """,
    )
