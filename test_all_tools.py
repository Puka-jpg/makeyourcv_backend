import asyncio
import uuid
from adk.tools.state_tools import (
    init_resume_session, 
    fetch_resume_data, 
    store_job_description,
    store_tailored_content_json,
    store_tailored_resume_valid_yaml,
    store_resume_text
)
from google.adk.tools import ToolContext
from db import sessionmanager
from models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Mock ToolContext
class MockToolContext:
    def __init__(self):
        self.state = {}

async def test_all_lazy_init_tools():
    # Force reset session factory to ensure lazy init is tested
    if sessionmanager.engine:
        await sessionmanager.close()
    sessionmanager.session_factory = None
    sessionmanager.engine = None
    
    print("\n--- Starting Lazy Init Test for ALL Tools ---")
    print(f"Pre-check: session_factory is {sessionmanager.session_factory}")

    tool_context = MockToolContext()
    
    # 1. Test init_resume_session (Should trigger lazy init)
    print("\n[1] Testing init_resume_session...")
    init_res = await init_resume_session(tool_context=tool_context)
    if init_res["status"] != "success":
        print(f"FAILED init_resume_session: {init_res}")
        return
    print(f"SUCCESS: {init_res['message']}")
    
    # Verify DB is linked
    if not sessionmanager.session_factory:
        print("CRITICAL: Session factory still None after init_resume_session!")
        return
    
    # 2. Test store_resume_text
    print("\n[2] Testing store_resume_text...")
    txt_res = await store_resume_text("Simulated Resume Content", tool_context)
    print(f"Result: {txt_res}")
    
    # 3. Test store_job_description
    print("\n[3] Testing store_job_description...")
    jd_res = await store_job_description("Simulated Job Description", tool_context)
    print(f"Result: {jd_res}")
    
    # 4. Test fetch_resume_data (Should retrieve what we just stored)
    # Force close and reopen to test lazy init AGAIN? No, reuse session for now.
    # But let's verify fetch works.
    print("\n[4] Testing fetch_resume_data...")
    fetch_res = await fetch_resume_data(tool_context)
    if fetch_res["status"] == "success":
        print("SUCCESS: Data retrieved")
        print(f"- Raw Text: {fetch_res.get('raw_resume_text')}")
        print(f"- Job Desc: {fetch_res.get('job_description')}")
    else:
        print(f"FAILED fetch_resume_data: {fetch_res}")

    await sessionmanager.close()
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_all_lazy_init_tools())
