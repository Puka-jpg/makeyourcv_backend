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

            # Extract text preview from content if available
            text_preview = None
            if has_content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_preview = (
                            part.text[:100] if len(part.text) > 100 else part.text
                        )
                        break

            # Log every event for debugging
            logger.info(
                "Agent event received",
                extra={
                    "event_num": event_count,
                    "author": author,
                    "is_final": is_final,
                    "has_content": has_content,
                    "num_parts": len(event.content.parts) if has_content else 0,
                    "text_preview": text_preview,
                },
            )

            # Collect any text from this event
            if event.content and event.content.parts:
                for i, part in enumerate(event.content.parts):
                    part_type = type(part).__name__
                    has_text = hasattr(part, "text") and part.text
                    has_func = hasattr(part, "function_call") and part.function_call
                    has_tool_resp = (
                        hasattr(part, "function_response") and part.function_response
                    )

                    logger.info(
                        "Event part details",
                        extra={
                            "event_num": event_count,
                            "part_num": i,
                            "part_type": part_type,
                            "has_text": has_text,
                            "text_length": len(part.text) if has_text else 0,
                            "text_content": part.text if has_text else None,
                            "function_call": part.function_call.name
                            if has_func
                            else None,
                            "function_response": "present" if has_tool_resp else None,
                        },
                    )

                    if has_text:
                        all_text_responses.append(part.text)
                        logger.info(
                            "Collected text response",
                            extra={
                                "total_responses": len(all_text_responses),
                                "text_preview": part.text[:100],
                            },
                        )

            # Also process for logging
            response = await process_agent_response(event)
            if response:
                final_response_text = response
                logger.info(
                    "[FINAL_RESPONSE_SET] Final response captured",
                    extra={"response_preview": response[:100] if response else None},
                )

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
            "text_responses_collected": len(all_text_responses),
            "has_final_response": final_response_text is not None,
            "all_responses_preview": [r[:50] for r in all_text_responses]
            if all_text_responses
            else [],
        },
    )

    if final_response_text:
        return final_response_text
    elif all_text_responses:
        return all_text_responses[-1].strip()

    return None
