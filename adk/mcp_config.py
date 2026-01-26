"""
Shared MCP Toolset Configuration.

Provides a single, reusable MCP toolset factory that can be used by any agent.
Avoids duplication of stdio/SSE configuration across agents.

MCP_MODE options:
- "local": Uses stdio transport to spawn MCP server as subprocess
- "remote": Uses SSE transport to connect to running MCP server
- "disabled": No MCP tools available
"""

from typing import Optional

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import SseConnectionParams
from mcp import StdioServerParameters

from settings import settings
from utils.logger import get_logger

logger = get_logger()


def get_mcp_toolset() -> Optional[McpToolset]:
    """
    Returns the appropriate MCP toolset based on settings.MCP_MODE.

    Creates a NEW instance each time to support per-request isolation and error recovery.
    """
    mcp_mode = settings.MCP_MODE.lower()

    if mcp_mode == "disabled":
        logger.info("MCP is disabled, skipping MCP toolset")
        return None

    try:
        if mcp_mode == "local":
            logger.info("Configuring MCP in LOCAL (stdio) mode")
            args = settings.RENDER_CV_MCP_ARGS.split(",")
            return McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=settings.RENDER_CV_MCP_COMMAND,
                        args=args,
                        cwd=settings.RENDER_CV_MCP_CWD,
                    ),
                ),
            )
        elif mcp_mode == "remote":
            logger.info(
                "Configuring MCP in REMOTE (SSE) mode",
                extra={"url": settings.RENDER_CV_MCP_URL},
            )
            return McpToolset(
                connection_params=SseConnectionParams(url=settings.RENDER_CV_MCP_URL)
            )
        else:
            logger.warning("Unknown MCP_MODE, disabling MCP", extra={"mode": mcp_mode})
            return None

    except Exception as e:
        logger.error(
            "Failed to initialize MCP toolset",
            extra={"error": str(e), "mode": mcp_mode},
        )
        return None


def build_tools_with_mcp(local_tools: list) -> list:
    """
    Build a tools list that includes local tools plus MCP toolset if available.

    Args:
        local_tools: List of local tool functions to include

    Returns:
        Combined list of local tools and MCP toolset (if enabled)
    """
    tools = list(local_tools)  # Copy to avoid mutation

    mcp_toolset = get_mcp_toolset()
    if mcp_toolset:
        tools.append(mcp_toolset)

    return tools
