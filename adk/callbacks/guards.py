from typing import Any, Dict, Optional

from google.adk.events import Event
from google.genai import types

from utils.logger import get_logger

logger = get_logger()

__all__ = ["guard_agent_execution", "before_agent_guard"]

CHECKPOINT_MAP: Dict[str, str] = {
    "parser_agent": "raw_resume_text",
    "job_analysis_agent": "raw_job_description",
    "get_schema_agent": "rendercv_schema_json",
    "job_tailoring_agent": "tailored_resume_valid_yaml",
}


async def before_agent_guard(callback_context: Any) -> Optional[Event]:
    """
    Checks if agent work is already done. Returns Event to skip if so.
    """
    agent_name = callback_context.agent_name
    state = callback_context.state

    required_key = CHECKPOINT_MAP.get(agent_name)
    if not required_key:
        return None

    if state.get(required_key):
        logger.info("Checkpoint HIT: Skipping ", extra={"agent_name": agent_name})
        msg = f"CHECKPOINT: {agent_name} completed. Data found in state."

        if hasattr(callback_context, "_invocation_context"):
            callback_context._invocation_context.end_invocation = True

        return Event(content=types.Content(role="model", parts=[types.Part(text=msg)]))

    return None


def guard_agent_execution() -> Dict[str, Any]:
    return {"before_agent": before_agent_guard}
