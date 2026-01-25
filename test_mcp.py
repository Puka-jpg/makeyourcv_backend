
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from settings import settings

async def main():
    print(f"MCP Mode: {settings.MCP_MODE}")
    command = settings.RENDER_CV_MCP_COMMAND
    args = settings.RENDER_CV_MCP_ARGS.split(",")
    cwd = settings.RENDER_CV_MCP_CWD
    
    print(f"Command: {command}")
    print(f"Args: {args}")
    print(f"CWD: {cwd}")
    
    if settings.MCP_MODE != "local":
        print("Skipping local test.")
        return

    server_params = StdioServerParameters(
        command=command,
        args=args,
        cwd=cwd,
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                print("\n--- Available Tools ---")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description[:50]}...")
                    
                resources = await session.list_resources()
                print("\n--- Available Resources ---")
                for resource in resources.resources:
                    print(f"- {resource.name} ({resource.uri})")

    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
