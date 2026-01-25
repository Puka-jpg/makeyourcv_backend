"""ADK Callbacks for Resume Builder."""

from adk.callbacks.caching import cache_tool_results
from adk.callbacks.guards import guard_agent_execution


def get_combined_callbacks():
    """
    Merge caching and guard callbacks for agents that need both.

    Returns:
        Dictionary with before_tool, after_tool, and before_agent callbacks.
    """
    callbacks = {}
    callbacks.update(cache_tool_results())
    callbacks.update(guard_agent_execution())
    return callbacks


__all__ = ["cache_tool_results", "guard_agent_execution", "get_combined_callbacks"]
