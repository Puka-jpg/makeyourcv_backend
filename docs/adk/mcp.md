# Model Context Protocol (MCP) in ADK

And Model Context Protocol (MCP) is an open standard that enables AI models to interact with server-side data and tools safely. ADK provides first-class support for consuming MCP servers.

## Key Components

1.  **`McpToolset`**: Connects to an MCP server and exposes its capabilities (resources, tools) to the agent.
2.  **`McpInstructionProvider`**: Fetches prompts from an MCP server to use as agent instructions.

## 1. Using MCP Tools (`McpToolset`)

The `McpToolset` allows you to connect to an MCP server (local or remote) and register its tools with your ADK agent.

### Configuration

You can connect via **Stdio** (local processes) or **SSE** (Server-Sent Events over HTTP).

#### Stdio Connection (e.g., Local Node/Python Scripts)

Connect to a local MCP server running as a subprocess.

```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters, StdioConnectionParams

# Configure connection to a local Filesystem MCP server
fs_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/home/user/files"],
        env={"PATH": "/usr/bin"} # Optional env vars
    )
)

# Create the toolset
fs_toolset = McpToolset(
    connection_params=fs_connection,
    tool_filter=["read_file", "list_directory"] # Optional whitelist
)

# Add to agent
agent = LlmAgent(tools=[fs_toolset])
```

#### SSE Connection (Remote Servers)

Connect to a remote MCP server running over HTTP.

```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

remote_connection = SseConnectionParams(
    url="http://localhost:8000/sse",
    headers={"Authorization": "Bearer token"}
)

remote_toolset = McpToolset(connection_params=remote_connection)
```

## 2. Using MCP Prompts (`McpInstructionProvider`)

MCP servers can define **Prompts**—templates that help guide the model. You can reuse these prompts as your agent's system instructions.

```python
from google.adk.agents.mcp_instruction_provider import McpInstructionProvider

# Define provider
prompt_provider = McpInstructionProvider(
    connection_params=fs_connection,
    prompt_name="summarize_file" # Name of the prompt in MCP server
)

# Set as agent instruction
# ADK will fetch the prompt content at runtime
agent = LlmAgent(
    instruction=prompt_provider
)
```

## Features

### filtering
You can filter which tools from the MCP server are exposed to the agent.
*   **List**: Pass a list of tool names (`tool_filter=['a', 'b']`).
*   **Predicate**: Pass a function `func(tool_name) -> bool`.

### Authentication
`McpToolset` supports `AuthScheme` and `AuthCredential` if the MCP server requires complex authentication flows.

### Architecture

`McpToolset` manages an internal `MCPSessionManager`. It handles:
*   **Session Pooling**: Reuses connections based on headers/params.
*   **Auto-Reconnect**: Retries operations if the session drops.
*   **Cleanup**: Ensures subprocesses are killed when `await toolset.close()` is called.
