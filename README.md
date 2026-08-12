# Central Consumer Intelligence Engine — MVP

A locally runnable autonomous market-intelligence MVP. Steps 1–15 are implemented incrementally, while the Consumer and Ingredient/Product specialist agents remain explicit placeholders.

## Architecture

```text
Scheduler
   ↓
RSS / Reddit collectors
   ↓
sources
   ↓
normalize + deduplicate
   ↓
signals + embeddings
   ↓
trend detection
   ↓
trends
   ↓
LangGraph
   ├── Trend Agent              ← implemented
   ├── Consumer Agent           ← placeholder
   └── Ingredient Agent         ← placeholder
             ↓
      India Relevance Agent
             ↓
      Business Opportunity Agent
             ↓
         Aggregator
             ↓
        Confidence Gate
        ├── high   → Slack
        ├── medium → HITL webhook / review
        └── low    → dropped
```

## Steps 8–15

- **8:** LangGraph fan-out/fan-in orchestration with typed state and specialist interfaces.
- **9:** India Relevance Agent using NVIDIA NIM.
- **10:** Business Opportunity Agent using NVIDIA NIM.
- **11:** Evidence Aggregator using NVIDIA NIM.
- **12:** Configurable confidence gate.
- **13:** `agent_events` logging for execution time, tokens and estimated cost.
- **14:** Slack for high-confidence insights and generic HITL webhook for medium-confidence insights.
- **15:** `all` command runs the end-to-end loop; `schedule` runs it periodically.

LangGraph supports fan-out/fan-in execution, so the three specialist nodes can execute in the same super-step before the India Relevance node consumes their outputs. citeturn1search0turn1search1

NVIDIA NIM exposes an OpenAI-compatible `/v1/chat/completions` API, which is why the MVP uses the OpenAI Python client as a thin NIM adapter. citeturn0search0turn0search1

## Setup

```bash
docker compose up -d postgres
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e .
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

alembic upgrade head
```

Set at least:

```env
NIM_API_KEY=your_nvidia_api_key
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_LLM_MODEL=your_available_nim_model
```

For a self-hosted NIM, use its local base URL, for example `http://localhost:8000/v1`. NVIDIA documents `/v1/models` as the way to find the exact served model name. citeturn0search1

Optional:

```env
SLACK_WEBHOOK_URL=...
HITL_WEBHOOK_URL=...
NIM_EMBEDDING_MODEL=...
NIM_EMBEDDING_BASE_URL=...
NIM_EMBEDDING_API_KEY=...
```

If `NIM_EMBEDDING_MODEL` is empty, the MVP falls back to `sentence-transformers/all-MiniLM-L6-v2`.

## Commands

```bash
python -m app.main collect
python -m app.main signals
python -m app.main trends
python -m app.main agent
python -m app.main graph
python -m app.main all
python -m app.main schedule
```

`graph` runs Steps 8–14 for the highest-scoring existing trend. `all` performs collection → signal extraction → trend detection → full agent graph.

## Confidence routing

Configured with:

```env
CONFIDENCE_HIGH_THRESHOLD=0.80
CONFIDENCE_MEDIUM_THRESHOLD=0.55
MINIMUM_EVIDENCE_QUALITY=0.60
```

The gate is deliberately conservative: a high model confidence score cannot pass if evidence quality is below the configured minimum.

## Database

Tables:

- `sources`
- `signals`
- `trends`
- `insights`
- `agent_events`

`insights.evidence` keeps the structured agent outputs needed to inspect why an insight was generated.

## Testing

```bash
python -m pytest -q
python -m compileall -q app alembic tests
```

The included tests cover the confidence gate and Pydantic agent contracts. Full end-to-end execution requires PostgreSQL, source connectivity, and a valid NVIDIA NIM credential/model.
