# ADK Agents

Agents are the core building blocks of ADK applications. They encapsulate logic, model configuration, and tools to perform tasks.

## LlmAgent

The `LlmAgent` is the primary agent type, powered by a Large Language Model (LLM).

### Configuration

Agents are configured using `LlmAgentConfig` but are typically instantiated directly via the `LlmAgent` class in code.

```python
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.llm_agent_config import LlmAgentConfig

agent = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",  # Defaults to system preference
    instruction="You are a senior researcher. Use tools to find facts.",
    tools=[google_search_tool],
)
```

### Instructions

Instructions guide the agent's behavior. ADK supports both dynamic and static instructions.

#### Dynamic Instructions (`instruction`)
Can contain placeholders interpolated at runtime from the session state.

```python
# State: {'user_name': 'Alice'}
agent.instruction = "Help {user_name} with their query."
```

#### Static Instructions (`static_instruction`)
Content that remains constant across invocations. This is optimized for **Context Caching**.

```python
from google.genai import types

agent.static_instruction = types.Content(
    role="system",
    parts=[types.Part.from_text("You are a helpful assistant serving various users.")]
)
```

### Delegation

Agents can transfer control to other agents. By default, an agent can transfer to:
1.  **Peer Agents**: Agents at the same level in the hierarchy.
2.  **Parent Agent**: Returning control up the stack.

**Controlling Delegation:**

```python
agent = LlmAgent(
    ...,
    disallow_transfer_to_peers=True,   # Isolate from siblings
    disallow_transfer_to_parent=True   # Force agent to finish task itself
)
```

## Agent Lifecycle

1.  **Invocation**: Agent receives the user message or delegation event.
2.  **Reasoning**: LLM generates a response or tool call.
3.  **Tool Execution**: If a tool is called, it runs, and results are fed back.
4.  **Response**: Final text is returned to the user or delegating agent.
