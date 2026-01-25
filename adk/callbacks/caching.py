"""
Caching callbacks for Resume Builder.

Implements before_tool and after_tool callbacks to cache expensive operations
like schema fetching and template retrieval.
"""

from typing import Any, Dict, Optional

from utils.logger import get_logger

logger = get_logger()

CACHE_CONFIG = {
    "get_schema": "cache:rendercv_schema",
    "get_templates": "cache:rendercv_templates",
    "extract_resume_text_tool": "cache:resume_text",
}


async def before_tool_cache(**kwargs) -> Optional[Dict[str, Any]]:
    """
    Before tool callback - check cache before executing tool.

    If cached result exists, returns it to skip tool execution.
    Otherwise returns None to proceed with tool execution.

    Args:
        **kwargs: ADK passes tool, args, context, etc.

    Returns:
        Cached result dict if found, None otherwise
    """
    tool_context = kwargs.get("context") or kwargs.get("tool_context")
    tool = kwargs.get("tool")

    if not tool_context:
        return None

    tool_name = tool.name if tool and hasattr(tool, "name") else str(tool)

    cache_key = CACHE_CONFIG.get(tool_name)
    if not cache_key:
        return None

    cached_result = tool_context.state.get(cache_key)
    if cached_result:
        logger.info(
            "Cache HIT for tool '%s'",
            tool_name,
            extra={"cache_key": cache_key},
        )
        return cached_result

    logger.info(
        "Cache MISS for tool '%s'",
        tool_name,
        extra={"cache_key": cache_key},
    )
    return None


async def after_tool_cache(**kwargs) -> None:
    """
    After tool callback - store tool result in cache.

    Args:
        **kwargs: ADK passes tool, result, context, etc.
    """
    tool_context = kwargs.get("context") or kwargs.get("tool_context")
    tool = kwargs.get("tool")
    result = kwargs.get("result")

    if not tool_context or not tool:
        return

    tool_name = tool.name if hasattr(tool, "name") else str(tool)

    cache_key = CACHE_CONFIG.get(tool_name)
    if not cache_key:
        return

    # Store result in state cache
    tool_context.state[cache_key] = result
    logger.info(
        "Cached result for tool '%s'",
        tool_name,
        extra={"cache_key": cache_key, "result_type": type(result).__name__},
    )


def cache_tool_results():
    """
    Returns callback configuration dict for caching.

    Usage in Runner:
        runner = Runner(
            agent=my_agent,
            callbacks=cache_tool_results()
        )
    """
    return {"before_tool": before_tool_cache, "after_tool": after_tool_cache}
