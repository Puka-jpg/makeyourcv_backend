# Workflows

ADK provides specialized agents to orchestrate complex logic flows. These "Workflow Agents" manage sub-agents in specific patterns.

## Sequential Agent

Executes a list of sub-agents one after another in a linear pipeline.

**Behavior**:
*   Agent 1 runs -> finishes -> output becomes context for Agent 2.
*   **Live Mode**: Waits for a `task_completed` signal.

**Configuration**:
```python
from google.adk.agents.sequential_agent import SequentialAgent

pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[extractor, transformer, loader]
)
```

## Parallel Agent

Executes multiple sub-agents concurrently.

**Behavior**:
*   The `InvocationContext` is branched for each sub-agent.
*   Outputs are merged back into the main event stream.
*   Useful for independent research tasks or multi-perspective analysis.

**Configuration**:
```python
from google.adk.agents.parallel_agent import ParallelAgent

analyst = ParallelAgent(
    name="analyst_group",
    sub_agents=[financial_analyst, tech_analyst, market_analyst]
)
```

## Loop Agent

Iterates over sub-agents until a termination condition is met.

**Termination Conditions**:
1.  **Max Iterations**: `max_iterations` config hit.
2.  **Escalation**: A sub-agent returns an event with `escalate=True`.

**Configuration**:
```python
from google.adk.agents.loop_agent import LoopAgent

refiner_loop = LoopAgent(
    name="refiner",
    sub_agents=[drafter, reviewer],
    max_iterations=3
)
```

### Escalate Tool (Exit Loop)
The `reviewer` agent needs a way to stop the loop. ADK provides `exit_loop_tool` or you can instruct the model to "escalate" if satisfied.
