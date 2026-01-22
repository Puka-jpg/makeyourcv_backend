# ADK Tools

Tools provide agents with capabilities to interact with the external world, such as searching the web, querying databases, or executing code.

## Defining Tools

### Function-based Tools
The simplest way to define a tool is using a python function with type hints and a docstring.

```python
def calculate_sum(a: int, b: int) -> int:
    """Calculates the sum of two integers.

    Args:
        a: First integer.
        b: Second integer.
    """
    return a + b
```

### Class-based Tools
Inherit from `BaseTool` for more complex logic.

```python
from google.adk.tools.base_tool import BaseTool
from google.genai import types

class MyTool(BaseTool):
    def _get_declaration(self):
        return types.FunctionDeclaration(
            name="my_tool",
            description="Does something cool",
            parameters=...
        )

    async def run_async(self, args, tool_context):
        return "Result"
```

## Built-in Tools

ADK ships with several built-in tools:
*   `GoogleSearchTool`: Performs Google searches (Gemini models only).
*   `CodeExecutionTool`: Executes Python code safely.

## Agent as a Tool (`AgentTool`)

This pattern allows you to encapsulate a sub-agent as a tool. The parent agent sees it as a single function call, while the sub-agent performs complex multi-turn reasoning internally.

**Optimization**: Use `include_plugins=False` to isolate the sub-agent's execution environment.

```python
from google.adk.tools.agent_tool import AgentTool

# 1. Define the sub-agent
specialist = LlmAgent(name="chart_generator", ...)

# 2. Wrap it as a tool
specialist_tool = AgentTool(agent=specialist)

# 3. Give it to the manager
manager = LlmAgent(tools=[specialist_tool])
```

**Output Handling**:
If the sub-agent has an `output_schema`, `AgentTool` will enforce that structure and return it as a JSON dictionary to the parent.
