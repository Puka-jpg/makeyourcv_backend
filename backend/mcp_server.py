from mcp.server.fastmcp import FastMCP

from db import sessionmanager
from tools.rendercv_tools import generate_resume_pdf
from tools.resume_tools import get_user_profile_tool, parse_and_save_cv
from utils.logger import get_logger

logger = get_logger()

# Initialize FastMCP Server
mcp = FastMCP("ResumeBuilderMCP")

# Register Tools
mcp.add_tool(parse_and_save_cv)
mcp.add_tool(get_user_profile_tool)
mcp.add_tool(generate_resume_pdf)

if __name__ == "__main__":
    # Initialize DB (sync)
    sessionmanager.init_db()
    logger.info("Database initialized for MCP Server.")

    # Run the server
    mcp.run()
