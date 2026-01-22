# Advanced Features

## Structured Outputs

You can force an agent to output structured data (JSON) instead of unstructured text. This is powered by Pydantic models.

**Setup**:
```python
from pydantic import BaseModel

class Receipt(BaseModel):
    total: float
    items: list[str]

agent = LlmAgent(
    ...,
    output_schema=Receipt,
    output_key="extracted_receipt" # Saves result to state automatically
)
```

**Constraints**:
*   When `output_schema` is set, the agent **CANNOT** use tools. It will only reason and produce the object.
*   If you need tools *and* structured output, use a `SequentialAgent`: [ToolAgent] -> [StructuringAgent].

## Callbacks

Callbacks allow you to hook into the runtime lifecycle to modify calls or log data.

### Types
*   **Model Callbacks**: `before_model`, `after_model`
*   **Tool Callbacks**: `before_tool`, `after_tool`

### Example: Profanity Filter

```python
async def profanity_filter(ctx: CallbackContext, response: LlmResponse):
    if "bad_word" in response.text:
        return types.Content(parts=[types.Part.from_text("Response filtered.")])
    return None # Proceed as normal

agent.after_model_callback = profanity_filter
```

## Live Mode

ADK supports real-time multimodal interaction suitable for voice/video bots.

**Implementation**:
*   Use `agent._run_live_impl`.
*   Requires a `LiveRequestQueue` to push audio chunks.
*   Supports full-duplex communication with 'barge-in' (interruption).
