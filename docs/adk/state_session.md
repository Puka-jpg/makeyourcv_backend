# State & Session Management

ADK applications are stateful. The framework manages conversation history and shared data across agent interactions.

## Session

A `Session` represents a continuous interaction thread with a user. It contains:
1.  **Events**: The history of messages, tool calls, and system events.
2.  **State**: A key-value store shared by all agents in the session.

### Session Services

The `Runner` uses a `BaseSessionService` to manage persistence.

**In-Memory (Development)**
```python
from google.adk.sessions.in_memory_session_service import InMemorySessionService
svc = InMemorySessionService()
```

**Database (Production)**
Used for persisting sessions to disk/DB.
```python
from google.adk.sessions.sqlite_session_service import SqliteSessionService
svc = SqliteSessionService("app.db")
```

## Shared State

State allows agents to share context without passing it in conversation text.

### Accessing State

**In Instructions:**
```python
# Interpolates state['order_id']
agent.instruction = "The current order ID is {order_id}."
```

**In Tools (`ToolContext`):**
Tools receive a `tool_context` argument.

```python
def update_shipping(address: str, tool_context):
    tool_context.state['shipping_address'] = address
    return "Updated"
```

## Artifacts

Artifacts are large data objects (PDFs, Images, CSVs) attached to a session. They are stored separately from the conversation text to optimize context window usage.

**Loading Artifacts (in Callbacks/Tools):**
```python
async def analyze_report(filename: str, tool_context):
    data = await tool_context.load_artifact(filename)
    # process data...
```
