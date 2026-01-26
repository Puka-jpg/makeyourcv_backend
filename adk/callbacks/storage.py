from typing import Any

from utils.logger import get_logger

logger = get_logger()


async def persist_parsed_resume(callback_context: Any) -> None:
    """
    Deprecated: Persistence is now handled by extract_resume_text_tool.
    Kept for backward compatibility during refactor.
    """
    pass


async def persist_job_description_callback(callback_context: Any) -> None:
    """
    Deprecated: Persistence is now handled by store_job_description tool.
    """
    pass


async def persist_tailored_content_callback(callback_context: Any) -> None:
    """
    Deprecated: Persistence is now handled by store_tailored_content_json tool.
    """
    pass


async def persist_yaml_callback(callback_context: Any) -> None:
    """
    Deprecated: Persistence is now handled by store_tailored_resume_valid_yaml tool.
    """
    pass
