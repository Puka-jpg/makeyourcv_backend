# Agent Development Kit (ADK) User Guide

This guide provides a comprehensive reference for building agentic applications using the Google Agent Development Kit (ADK). It covers core architecture, component configuration, execution patterns, and advanced features.

## 1. Core Architecture

ADK uses a hierarchical, delegation-based architecture where a **Runner** executes a **Root Agent** within a **Session**.

### Key Concepts

*   **Agent**: The fundamental unit of logic. Agents can use tools, models, and sub-agents.
*   **Runner**: The engine that drives execution. It manages the event loop, connects services (memory, storage), and handles the agent lifecycle.
*   **Session**: Represents a stateful conversation thread. It persists history and shared state across turns.
*   **State**: A shared key-value store accessible by all agents in a session.
*   **Tools**: Functions or external services that agents can invoke.

---

## 2. Agents

Agents are defined by their configuration (`AgentConfig`) and implementation class. The most common type is `LlmAgent`.

### LlmAgent

A general-purpose agent driven by a Large Language Model.

**Configuration:**

```python
from google.adk.agents.llm_agent_config import LlmAgentConfig

sales_agent_config = LlmAgentConfig(
    model="gemini-1.5-pro", # Optional: Defaults to gemini-2.5-flash
    instruction="You are a helpful sales assistant. Use the state to track orders.",
    tools=[
        {"name": "lookup_inventory"}, # Reference to a registered tool
    ],
    # delegation controls
    disallow_transfer_to_peers=True, 
)
```

**Key Features:**

*   **Dynamic Instructions**: Instructions can contain placeholders `{variable}` that are interpolated from the session state at runtime.
*   **Static Instructions**: Use `static_instruction` for content that never changes (optimization for context caching).
*   **Delegation**: By default, agents can transfer control to any peer or sub-agent. Use `disallow_transfer_to_*` flags to restrict this.

### Workflow Agents

ADK provides specialized agents for orchestrating structured flows:

1.  **SequentialAgent**: Runs a list of sub-agents in a strict order.
    *   *Use case*: Data processing pipelines (e.g., Extract -> Transform -> Verify).
    *   *Live Mode*: Uses a special `task_completed` signal to advance steps.

2.  **ParallelAgent**: Runs sub-agents concurrently.
    *   *Implementation*: Uses `asyncio` to fan-out execution.
    *   *Isolation*: Each sub-agent runs in a branched `InvocationContext` (trace id: `parent.agent_name`).
    *   *Merge*: Events are merged back into the main stream as they occur.

3.  **LoopAgent**: Iterates over sub-agents until a condition is met.
    *   *Termination*: Stops when `max_iterations` is reached OR a sub-agent signals `escalate`.
    *   *Use case*: Draft-Review-Revise cycles.

---

## 3. Tools

Tools bridge agents to the outside world.

### Defining Tools

Tools can be simple Python functions or class-based `BaseTool` implementations.

**Function-based (Simplest):**

```python
def get_current_time():
    """Returns the current server time."""
    return datetime.now().isoformat()
```

**Class-based (Advanced):**
Inherit from `google.adk.tools.base_tool.BaseTool`.

### Agent as a Tool (`AgentTool`)

This wrapper allows an entire agent (and its sub-agents/tools) to be treated as a single tool call by another agent. This restricts the wrapped agent to a specific task and forces it to return its final response as a tool output string, rather than communicating directly with the user.

```python
from google.adk.tools.agent_tool import AgentTool

# Wrap an existing research agent
research_tool = AgentTool(
    agent=research_agent,
    exclude_plugins=False # Inherit parents plugins/context
)

# Parent agent can now "call" the researcher
manager_agent.tools.append(research_tool)
```

**Why usage this?**
*   To encapsulate complex behaviors (e.g., "Research Topic A") into a single atomic action.
*   To permit specific delegation paths in an otherwise flat structure.

---

## 4. State & Session Management

ADK uses a "Shared State" model. ALL agents in a session share access to a global `state` dictionary.

### Session Services

*   **`InMemorySessionService`**: Ideal for testing/dev. State is lost on restart.
*   **`DatabaseSessionService`** (e.g., `SqliteSessionService`): Persists state and event history to disk.

### Usage in Agents

Agents read/write state via instructions or tools.

**In Tool:**
```python
def set_user_name(name: str, tool_context: ToolContext):
    # Update shared state
    tool_context.state['user_name'] = name
    return f"Name set to {name}"
```

**In Instruction:**
```python
instruction="The user's name is {user_name}. Greet them by name."
```

### Context Caching & Artifacts

*   **Artifacts**: Large objects (files, images) are stored separately via `ArtifactService`. You can reference them in prompts.
*   **Context Caching**: Supported by `LlmAgent` to cache prefix static instructions and tools, reducing latency and cost.

---

## 5. Execution: The Runner

The `Runner` orchestrates the entire process.

### Basic Setup

```python
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

runner = Runner(
    app_name="my_app",
    agent=root_agent,
    session_service=InMemorySessionService()
)

# Async Execution
async for event in runner.run_async(
    user_id="user_123",
    session_id="session_abc",
    new_message=types.Content(role="user", parts=[types.Part.from_text("Hello")])
):
    print(event)
```

### Event Lifecycle

1.  **Ingestion**: User message is appended to the session.
2.  **Delegation**: Root agent decides to handle it or delegate.
3.  **Execution Loop**:
    *   Model is called.
    *   Tools are executed.
    *   Callbacks (`before_model`, `after_tool`, etc.) are triggered.
4.  **Compaction** (Optional): Events can be summarized to save context window.

---

## 6. Advanced Features

### Callbacks (Hooks)

ADK provides extensive hooks to intervene in the execution flow.

*   `before_model_callback`: Modify the prompt before it goes to the LLM.
*   `after_model_callback`: Intercept/modify the LLM's response.
*   `before_tool_callback`: Modify tool arguments or mock execution.
*   `on_tool_error_callback`: Handle exceptions gracefully.

**Callback Context (`CallbackContext`):**
Callbacks receive a `CallbackContext` object which provides access to:
*   `ctx.state`: Read/Write shared state.
*   `ctx.load_artifact()` / `ctx.save_artifact()`
*   `ctx.history`: Access previous events.

### Structured Output

Enforce JSON output schemas using Pydantic models.

```python
from pydantic import BaseModel

class EmailSchema(BaseModel):
    subject: str
    body: str

agent = LlmAgent(
    ...,
    output_schema=EmailSchema,
    output_key="last_generated_email" # Automatically save result to state
)
```

### Live Mode

ADK supports real-time multimodal interaction (audio/video).
*   `run_live_impl` handles streaming I/O.
*   `task_completed` tool is injected in sequential flows to signal manual handoffs in continuous streams.
