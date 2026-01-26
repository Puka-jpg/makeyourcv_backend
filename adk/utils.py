from google.genai import types

from utils.logger import get_logger

logger = get_logger()


async def process_agent_response(event):
    """Process and log agent response events."""
    final_response = None
    text_parts = []

    # Log specific parts for debugging and collect text
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "executable_code") and part.executable_code:
                logger.debug(
                    "Agent generated code:", extra={"code": part.executable_code.code}
                )
            elif hasattr(part, "code_execution_result") and part.code_execution_result:
                logger.debug(
                    "Code Execution Result:",
                    extra={"outcome": part.code_execution_result.outcome},
                )
            elif hasattr(part, "tool_response") and part.tool_response:
                logger.debug(
                    "Tool Response:", extra={"output": part.tool_response.output}
                )
            elif hasattr(part, "text") and part.text:
                text_parts.append(part.text)

    if event.is_final_response():
        if text_parts:
            final_response = "".join(text_parts).strip()
    elif text_parts and hasattr(event, "author") and event.author:
        logger.debug(
            "Intermediate text response",
            extra={
                "author": event.author,
                "text_preview": text_parts[0][:100] if text_parts else "",
            },
        )

    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    logger.info(
        "[AGENT_CALL_START] Running Query",
        extra={
            "query": query[:200] + "..." if len(query) > 200 else query,
            "user_id": user_id,
            "session_id": session_id,
        },
    )

    final_response_text = None
    all_text_responses = []
    event_count = 0

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            event_count += 1
            author = getattr(event, "author", "unknown")
            is_final = event.is_final_response()
            has_content = event.content is not None

            # Only log significant events (Final or Tool calls)
            if is_final or (
                has_content
                and event.content.parts
                and any(p.function_call for p in event.content.parts)
            ):
                logger.info(
                    "Agent Event",
                    extra={
                        "event_num": event_count,
                        "author": author,
                        "is_final": is_final,
                        "has_tool_call": True
                        if has_content
                        and any(p.function_call for p in event.content.parts)
                        else False,
                    },
                )

            # Collect any text from this event
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if hasattr(p, "text") and p.text:
                        all_text_responses.append(p.text)

            # Also process for logging/final response extraction
            response = await process_agent_response(event)
            if response:
                final_response_text = response

    except Exception as e:
        logger.exception(
            "[AGENT_CALL_ERROR] Error during agent call",
            extra={"error": str(e)},
        )
        raise e

    logger.info(
        "[AGENT_CALL_COMPLETE] Agent run complete",
        extra={
            "total_events": event_count,
            "has_final_response": final_response_text is not None,
        },
    )

    if final_response_text:
        return final_response_text
    elif all_text_responses:
        return all_text_responses[-1].strip()

    return None
