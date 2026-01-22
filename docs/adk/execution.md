# Execution & Runners

The `Runner` is the engine that drives your agentic application. It manages the event loop, coordinates services, and handles communication.

## The Runner

The `Runner` connects your `Root Agent` to the `Session` and `IO`.

### Initialization

```python
from google.adk.runners import Runner

runner = Runner(
    app_name="my_app",
    agent=my_root_agent,
    session_service=my_session_service,
    # Optional services
    memory_service=...,
    artifact_service=...,
)
```

### Running an Invocation

The `run_async` method processes a user turn.

```python
async for event in runner.run_async(
    user_id="user_1",
    session_id="session_1",
    new_message=types.Content(role="user", parts=[...])
):
    print(event)
```

## The Event Loop

ADK operates on an event-driven architecture.

1.  **User Input**: A `new_message` starts the loop.
2.  **Agent Logic**: The agent processes the input.
3.  **Event Generation**: The agent yields `Event` objects (e.g., `model_call`, `tool_call`).
4.  **Runner Handling**:
    *   If `tool_call`: Runner executes the tool and feeds the result back.
    *   If `delegation`: Runner switches context to the new agent.
5.  **Termination**: The loop ends when the agent produces a final answer or requires user input.

## `adk web` (CLI Runner)

For rapid prototyping, ADK includes a CLI that spins up a local web server (using chainlit/gradio under the hood).

**Usage:**
```bash
adk web --agent-module app.agent --agent-name root_agent
```

This commands looks for `root_agent` in `app/agent.py`.
