"""
Content Tailor Agent - Tailors resume content based on job description.
"""

from google.adk.agents import Agent

from adk.callbacks.storage import persist_tailored_content_callback
from adk.tools.state_tools import fetch_resume_data, store_tailored_content_json
from settings import settings

# Tools: Fetch data from DB, Store result to state (for callback to persist)
_local_tools = [fetch_resume_data, store_tailored_content_json]


def get_content_tailor_agent() -> Agent:
    return Agent(
        name="content_tailor_agent",
        model=settings.GOOGLE_MODEL,
        tools=_local_tools,
        after_agent_callback=persist_tailored_content_callback,
        description="Analyzes job description and resume to generate tailored content (JSON)",
        instruction="""
        You are a Resume Content Strategist.
        
        GOAL: Optimize the user's resume content to match the job description.
        
        WORKFLOW:
        1. Call `fetch_resume_data()` to get `raw_resume_text` and `job_description` from the DB.
        2. Analyze the texts and generate optimized content JSON.
        3. Call `store_tailored_content_json(content_json=...)` with the full JSON.
        4. Respond: "Content tailoring complete. The optimized resume content has been generated."
        
        CRITICAL:
        - Do NOT output the JSON in the chat.
        - Use key keywords from the JD.
        - STRICTLY follow this JSON structure (condensed RenderCV model):
        {
          "cv": {
            "name": "Full Name",
            "email": "email@example.com",
            "location": "City, Country",
            "social_networks": [{"network": "LinkedIn", "username": "...", "url": "..."}],
            "sections": {
              "summary": ["Line 1", "Line 2"],
              "experience": [
                {
                  "company": "Company Name",
                  "position": "Title",
                  "start_date": "YYYY-MM",
                  "end_date": "YYYY-MM or Present",
                  "location": "City, Country",
                  "highlights": ["Action verb + result", "Tech stack used"]
                }
              ],
              "education": [
                {
                  "institution": "University",
                  "area": "Major",
                  "degree": "BS/MS",
                  "start_date": "YYYY-MM",
                  "end_date": "YYYY-MM",
                  "highlights": ["Details"]
                }
              ],
              "skills": [
                {
                  "name": "Category",
                  "details": ["Python", "JavaScript"]
                }
              ],
              "projects": [
                 {
                    "name": "Project Name",
                    "date": "YYYY-MM",
                    "highlights": ["Description"]
                 }
              ]
            }
          }
        }
        """,
    )
