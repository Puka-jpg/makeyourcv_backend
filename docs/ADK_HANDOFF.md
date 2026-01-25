# ADK Resume Builder - Handoff Document

## Project Overview

**Resume Builder** - AI-powered resume tailoring system using Google ADK (Agent Development Kit) and RenderCV MCP server to generate professionally formatted, job-specific resumes.

**Tech Stack:**
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy
- **AI Framework:** Google ADK with multi-agent architecture
- **Resume Rendering:** RenderCV via MCP server
- **LLM:** Google Gemini models

---

## Recent Major Changes (Jan 2026)

### ✅ Architecture Refactoring (Completed)
- Removed obsolete `/api/cv_parser` route
- Cleaned up state schemas (removed predefined TypedDicts)
- Simplified CVParserService (43% code reduction)
- Migrated to ADK artifact management
- All agents updated with proper tool dependencies

### ✅ Workflow Improvements (Completed)
**Problem:** Chat/task flow was struggling with unpredictable execution and redundant operations.

**Solutions Implemented:**
1. **SequentialAgent Pipeline** ([`adk/agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agent.py))
   - Replaced LLM-driven orchestrator with deterministic pipeline
   - Fixed execution: parse → analyze → schema → tailor → format
   - 80%+ reduction in orchestration LLM calls

2. **Tool Caching Callbacks** ([`adk/callbacks/caching.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/callbacks/caching.py))
   - before_tool & after_tool callbacks for performance
   - Caches: schema, templates, resume text
   - 50%+ faster response times

3. **State Validation Guards** ([`adk/callbacks/guards.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/callbacks/guards.py))
   - before_agent callback validates prerequisites
   - Prevents invalid agent executions
   - Clear error messaging

4. **Simplified Orchestrator** ([`adk/agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agent.py))
   - Orchestrator handles UX, pipeline handles workflow
   - Cleaner separation of concerns

---


---

## ✅ COMPLETED: Runner Callbacks API Fix (Jan 25, 2026)

**Problem (Resolved):**
```python
# This was causing TypeError
runner = Runner(
    agent=root_agent,
    callbacks=get_callbacks()  # ❌ Invalid parameter
)
```

**Solution Applied:**
Callbacks are now registered on individual `Agent` instances using correct parameter names (`before_tool_callback`, `after_tool_callback`, `before_agent_callback`) instead of being passed to `Runner`.

**Verification:**
- ✅ Type checking passes (`just mypy`)
- ✅ Linting clean (`just format`)
- ✅ Application starts successfully (`just dev`)

**Details:** See [`docs/RUNNER_CALLBACKS_FIX.md`](file:///home/pukar-kafle/Documents/Resume-Builder/docs/RUNNER_CALLBACKS_FIX.md) for complete solution documentation.

---

## Agent Architecture

### Pipeline Flow (SequentialAgent)
```
resume_pipeline = SequentialAgent([
    parser_agent,           # Extracts text from PDF
    job_analysis_agent,     # Stores job description  
    get_schema_agent,       # Fetches RenderCV schema + templates
    job_tailoring_agent,    # Generates tailored YAML
    resume_formatter_agent  # Renders final PDF
])
```

### Individual Agents

**parser_agent** ([`adk/agents/parser_agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agents/parser_agent.py))
- Tool: `extract_resume_text_tool`
- Stores: `raw_resume_text` in state
- No MCP dependencies

**job_analysis_agent** ([`adk/agents/job_analysis_agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agents/job_analysis_agent.py))
- Tool: `store_job_description`
- Stores: `raw_job_description` in state

**get_schema_agent** ([`adk/agents/get_schema_agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agents/get_schema_agent.py))
- MCP Tools: `get_schema`, `get_templates` (from RenderCV server)
- Stores: `rendercv_schema_json`, `rendercv_templates` in state
- **Note:** Uses MCP for schema/template fetching

**job_tailoring_agent** ([`adk/agents/job_tailoring_agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agents/job_tailoring_agent.py))
- MCP Tool: `validate_yaml` (from RenderCV server)
- Stores: `tailored_resume_valid_yaml` in state
- Generates job-specific resume YAML

**resume_formatter_agent** ([`adk/agents/resume_formatter_agent.py`](file:///home/pukar-kafle/Documents/Resume-Builder/adk/agents/resume_formatter_agent.py))
- MCP Tool: `render_cv` (from RenderCV server)
- ADK Tools: `convert_yaml_to_rendercv_input`, `save_pdf_artifact`
- Outputs: PDF via ADK artifacts

---

## State Management

### Session State Keys
```python
{
    # File paths
    "resume_file_path": str,           # Uploaded resume location
    
    # Raw data
    "raw_resume_text": str,            # Extracted PDF text
    "raw_job_description": str,        # Job posting text
    
    # Schema & templates
    "rendercv_schema_json": str,       # RenderCV JSON schema
    "rendercv_templates": List[str],   # Available templates
    
    # Output
    "tailored_resume_valid_yaml": str, # Final YAML
    
    # Caching (managed by callbacks)
    "cache:rendercv_schema": dict,
    "cache:rendercv_templates": list,
    "cache:resume_text": str
}
```

---

## MCP Server Configuration

**RenderCV MCP Server** (`mcp_config.py`)
- Endpoint: Configure in environment
- Tools exposed: `get_schema`, `get_templates`, `render_cv`, `validate_yaml`
- Purpose: Professional resume generation from YAML

---

## API Endpoints

### Main Chat Endpoint
```
POST /api/v1/adk/chat
```
**Request:**
- `message`: str (user input)
- `file`: UploadFile (optional resume PDF)

**Response:**
```json
{
  "response": "string",
  "state": { /* session state */ }
}
```

**Session:** Forever session per user (`session_{user_id}`)

---

## File Structure

```
adk/
├── agent.py                    # SequentialAgent pipeline + orchestrator
├── agents/
│   ├── parser_agent.py
│   ├── job_analysis_agent.py
│   ├── get_schema_agent.py
│   ├── job_tailoring_agent.py
│   └── resume_formatter_agent.py
├── callbacks/                  # NEW
│   ├── __init__.py
│   ├── caching.py             # Tool result caching
│   └── guards.py              # State validation
├── tools/
│   ├── state_tools.py         # State management tools
│   ├── artifact_tools.py      # ADK artifact helpers
│   └── parser_tool.py         # PDF text extraction
├── routes.py                   # FastAPI endpoints
└── mcp_config.py              # MCP server setup
```

---

## Next Steps / Remaining Work

### 🔴 **IMMEDIATE: Fix Runner Callbacks**
- [ ] Research ADK callbacks registration API
- [ ] Update `adk/routes.py` with correct pattern
- [ ] Verify callbacks work (before_tool, after_tool, before_agent)

### Testing & Validation
- [ ] Test caching behavior (cache hit/miss)
- [ ] Test state validation guards
- [ ] End-to-end workflow test
- [ ] Performance benchmarking

### Nice-to-Have Enhancements
- [ ] Add retry logic for MCP failures
- [ ] Implement rate limiting per user
- [ ] Add telemetry/monitoring
- [ ] Create admin dashboard for session management

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/resumebuilder

# Google AI
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-2.0-flash-exp

# OpenAI (legacy, optional)
OPENAI_API_KEY=...

# App Config
DEBUG=1
SECRET_KEY=...
```

---

## Common Commands

```bash
# Development
just dev              # Run FastAPI dev server
just format           # Lint & format code
just mypy             # Type checking
just test             # Run tests

# Database
just migrate          # Run Alembic migrations
just upgrade          # Upgrade DB schema
```

---

## Key Learnings & Patterns

### ADK Best Practices Used
1. **SequentialAgent for deterministic workflows** - Perfect for linear pipelines
2. **Callbacks for cross-cutting concerns** - Caching, validation, logging
3. **State-based coordination** - Agents communicate via shared state
4. **MCP integration** - External tools via Model Context Protocol

### Architecture Decisions
- **Forever sessions** - Per-user session persistence
- **ADK artifacts** - Session-scoped file storage
- **Modular agents** - Each agent has single responsibility
- **Tool-based state management** - Explicit state storage tools

---

## Debugging Tips

### Check Session State
```python
from adk.memory import get_session_service
session = await session_service.get_session(
    app_name="agents",
    user_id=user_id,
    session_id=f"session_{user_id}"
)
print(session.state)
```

### Test Individual Agent
```python
from adk.agents.parser_agent import parser_agent
await parser_agent.run_async(invocation_context)
```

### Clear Cache
```python
# State keys starting with "cache:" can be manually cleared
del tool_context.state["cache:rendercv_schema"]
```

---

## Contact & Resources

**Documentation:**
- [ADK Docs](https://google.github.io/adk-docs/)
- [RenderCV Docs](https://docs.rendercv.com/)

**Project Repo:** Internal - contact team for access

---

**Last Updated:** Jan 25, 2026
**Status:** ⚠️ CRITICAL PERFORMANCE ISSUES - Latency > 5 mins

## 🔴 Current Situation & Architectural Faults (Jan 25, 2026)

**The Problem:**
Despite optimizations, the end-to-end resume generation workflow takes an unacceptable amount of time (5+ minutes) and sometimes hangs indefinitely. Logs show repeated `Sending out request` -> `Processing request` cycles without completion.

**Hypothesis:**
1.  **Massive Context Overload:** The `raw_resume_text` + `raw_job_description` + `rendercv_schema_json` (which is huge) + `rendercv_templates` creates a massive context window.
2.  **Internal Monologue Hallucination:** Even with "SILENT" instructions, the model might be generating the full 2000-line JSON/YAML internally before deciding to call the tool. This "thought process" burns tokens and time, and if it exceeds the output token limit, it might be truncating or looping.
3.  **Agent granularity:** Splitting `job_tailoring` into `content_tailor` + `yaml_formatter` doubled the number of heavy LLM calls. If `content_tailor` takes 2 mins to generate JSON, and `yaml_formatter` takes 3 mins to convert to YAML, the user waits 5 mins.
4.  **Schema Complexity:** The RenderCV schema is extremely strict and verbose. Feeding the raw JSON schema to the prompt consumes a vast amount of the context and cognitive load.

**Proposed Redesign (Urgent):**
1.  **Reduce Schema Size:** usage of `get_schema` is fetching the FULL schema. We should distill this into a "Lite" schema or just few-shot examples.
2.  **Streaming / Real-time Feedback:** The user stares at a spinner. We need to stream partial progress or "thinking" states.
3.  **Combine Agents (Smartly):** The split was good for logical separation but bad for latency. We might need a single "Smart Fills" agent that just fills a template rather than generating from scratch.
4.  **Faster Model:** Swith to `flash` is already done, but maybe we need to optimize *what* we send it.

**Action Item:**
- Analyze `adk/agents/get_schema_agent.py`. Are we sending the *entire* schema? Can we strip descriptions?
- Investigate `content_tailor_agent`. Is it re-writing the *entire* resume or just the summary? It should only touch what's needed.
