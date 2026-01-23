import asyncio
import os
import sys
from pathlib import Path

# Add backend to path if needed, or assume environment is set
# We need google.adk
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_agent():
    # 1. Setup & Configure Agent
    from agent.factory import create_agent
    agent = create_agent()
    
    # 3. Run Agent (Interactive Mode for testing)
    # We use a mocked runner loop here for demonstration/verification
    runner = Runner(
        app_name="makeyour-cv-agent",
        agent=agent,
        session_service=InMemorySessionService()
    )
    
    logger.info("Agent initialized. Starting chat session...")
    
    # Simple CLI loop
    session_id = "test-session-1"
    user_id = "test-user-1" # Mock user ID, in real app this comes from auth context
    
    # We need a way to input from stdin in this loop
    # For automated verification, we might just run one turn.
    # For now, let's just exit to prove initialization worked.
    logger.info("Agent setup complete.")

if __name__ == "__main__":
    asyncio.run(run_agent())
