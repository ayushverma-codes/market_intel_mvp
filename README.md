# Central Consumer Intelligence Engine

> **An agentic MVP for continuously turning market signals into India-specific, evidence-backed business insights.**

## Challenge Context

This project was developed for the **Think9 AI & Intelligence Challenge**.

The challenge asks participants to design an AI/agentic system that can be
deployed centrally across Think9's 30+ consumer brands to solve a critical
business bottleneck or improve operational speed.

For this submission, I selected:

**Track 1 — Central Consumer Intelligence Engine**

The objective of this track is to design an autonomous system that
continuously ingests global trends, social signals, ingredients, and
consumer behaviours and proactively pushes actionable insights tailored
to the Indian market.

## 1. Why This Project?

Market research is often **static, slow, and reactive**. Analysts have to monitor fragmented sources such as news, social discussions, consumer conversations, product/ingredient signals, and competitor activity before they can identify an opportunity.

For a portfolio operating across many consumer brands, the problem is not simply a lack of information. The problem is **too much information and too little decision-ready intelligence**.

This project explores a different approach:

```text
External Signals
      ↓
Signal Processing
      ↓
Emerging Trends
      ↓
Specialist Analysis
      ↓
India Relevance
      ↓
Business Opportunity
      ↓
Evidence + Confidence
      ↓
Proactive Delivery
```

The goal is **not to build another market-summary dashboard**.

The goal is to build an intelligence layer that can answer:

> **What changed, why does it matter to Indian consumers, and what should the business do next?**


---

# 2. Design Process

The system was designed from the **business workflow first**, rather than starting with a preferred AI framework.

## Step 1 — Start with the real-world bottleneck

A consumer-intelligence analyst typically has to:

1. Monitor multiple external sources.
2. Collect potentially relevant signals.
3. Remove duplicates and irrelevant information.
4. Identify patterns across signals.
5. Determine whether a pattern is a genuine emerging trend.
6. Understand what consumers are saying or doing.
7. Identify associated products and ingredients.
8. Evaluate whether the trend is relevant to India.
9. Identify affected consumer segments.
10. Translate the trend into a business opportunity.
11. Decide how confident the business should be.
12. Communicate the insight to the relevant team.

The design therefore focuses on **compressing this workflow**, rather than simply adding an LLM to the end of it.

---

## Step 2 — Break the analyst workflow into decisions

A useful way to think about the system is as a sequence of questions:

| Decision | Question |
|---|---|
| Trend | Is something actually changing? |
| Evidence | Is the signal real or just noise? |
| Consumer | What are consumers saying or doing? |
| Product | Which products/formats are associated with it? |
| Ingredient | Which ingredients are involved? |
| India | Does the trend matter to Indian consumers? |
| Segment | Who is affected? |
| Business | What could a company do about it? |
| Confidence | Is there enough evidence to act? |

This leads to the core design principle:

> **Agents should exist because there are distinct analytical responsibilities — not simply because a system is supposed to be "multi-agent".**

---

# 3. From Signals to Intelligence

The system deliberately separates four levels:

```text
SIGNAL
A single observation from an external source
        ↓
TREND
A repeated / growing pattern across signals
        ↓
INSIGHT
A validated interpretation of why the trend matters
        ↓
ACTION
A concrete business recommendation
```

For example:

```text
Multiple discussions mentioning protein + snacks
                    ↓
       High-protein snack trend
                    ↓
 Stronger relevance among Indian urban consumers
                    ↓
 Opportunity for an affordable protein snack
```

This distinction is important because **a summary of signals is not the same thing as intelligence**.

---

# 4. Why Agentic AI?

A conventional dashboard can tell a team:

> "Protein-related discussions increased."

A generic LLM can tell a team:

> "These articles discuss growing interest in protein."

The proposed system goes further:

> **"Is this a meaningful trend, does it matter to India, what business opportunity does it create, and how strong is the evidence?"**

These are different analytical decisions.

The MVP therefore uses a workflow of specialist reasoning components:

```text
                 Candidate Trend
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Trend       Consumer     Ingredient
       Agent        Agent         Agent
          │            │            │
          └────────────┼────────────┘
                       ↓
              India Relevance Agent
                       ↓
             Business Opportunity Agent
                       ↓
                   Aggregator
                       ↓
                Confidence Gate
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
            HIGH              MEDIUM/LOW
              ↓                 ↓
          Auto-delivery       Review / Ignore
```

The current code already establishes interfaces for the Consumer and Ingredient/Product agents; these are intentionally kept as placeholders in the MVP while the Trend, India Relevance, Business Opportunity, and Aggregator reasoning paths are implemented.

---

# 5. System Architecture

## High-level architecture

```text
                         EXTERNAL WORLD
                              │
                 ┌────────────┼────────────┐
                 ↓            ↓            ↓
               RSS          Reddit      Future Sources
                 │            │
                 └────────────┼────────────┘
                              ↓
                       INGESTION LAYER
                              ↓
                   NORMALIZATION + DEDUP
                              ↓
                         PostgreSQL
                              ↓
                    SIGNAL EXTRACTION
                              ↓
                     EMBEDDINGS / pgvector
                              ↓
                      TREND DETECTION
                              ↓
                        LANGGRAPH
                       ORCHESTRATOR
                              ↓
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
        Trend Agent     Consumer Agent    Ingredient Agent
        implemented       placeholder       placeholder
             │                │                │
             └────────────────┼────────────────┘
                              ↓
                   India Relevance Agent
                              ↓
                 Business Opportunity Agent
                              ↓
                         Aggregator
                              ↓
                      Confidence Gate
                              ↓
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
            HIGH            MEDIUM             LOW
             ↓                ↓                ↓
          Slack          HITL webhook        No push
```

## Main components

### 1. Ingestion

Collectors currently support:

- RSS feeds
- Reddit public JSON endpoints

Each source record stores:

- source
- URL
- timestamp
- content
- source type
- credibility

The collector interfaces are intentionally small so additional sources can be added without changing the downstream pipeline.

### 2. Normalization and deduplication

Raw sources are normalized before intelligence processing.

The pipeline removes duplicate records using:

- URL-based deduplication
- normalized content hashing

This prevents the same event being counted repeatedly.

### 3. Signal extraction

The system converts source documents into domain-oriented signals.

For the current MVP, extraction is deliberately lightweight and uses a controlled market-intelligence vocabulary around concepts such as:

- food
- snacks
- protein
- nutrition
- pricing
- demand
- supply
- ingredients
- packaging
- retail
- consumer behaviour

Each signal can also receive an embedding.

### 4. Trend detection

Trend detection is performed before expensive LLM reasoning.

The detector considers:

- signal frequency
- recent activity
- growth
- velocity
- spike behaviour
- source credibility

A weighted trend score is then used to rank candidate trends.

This creates an important **reasoning funnel**:

```text
Many raw sources
      ↓
Signals
      ↓
Candidate trends
      ↓
Top trends
      ↓
LLM reasoning
```

The expensive reasoning layer therefore operates on a much smaller search space.

---

# 6. Agent Responsibilities

## Trend Agent

**Question:**

> Is this actually a meaningful trend?

It receives the detected trend, trend score, growth rate, and supporting evidence.

It returns structured output containing:

- trend
- trend strength
- evidence
- supporting signal count
- confidence

---

## Consumer Agent

**Question:**

> What are consumers actually saying or doing?

The interface exists in the current architecture but is intentionally a placeholder for the next iteration.

Future responsibilities include:

- consumer discussions
- preferences
- complaints
- behavioural signals
- audience characteristics

---

## Ingredient / Product Agent

**Question:**

> Which ingredients, products, or formats are associated with the trend?

The current interface is also a placeholder.

The intended extension is:

```text
Trend
  ↓
Ingredient
  ↓
Product Format
  ↓
Consumer Need
```

---

## India Relevance Agent

This is one of the most important reasoning layers.

A global trend is **not automatically an Indian opportunity**.

The agent evaluates the available evidence around:

- cultural fit
- affordability
- availability
- existing Indian behaviour
- regional considerations
- target consumer segments

Output includes:

- India relevance score
- reasoning
- target segments
- regional notes

---

## Business Opportunity Agent

**Question:**

> What could a consumer business do about this?

The agent translates the analysed trend into possible:

- product opportunities
- marketing opportunities
- pricing opportunities
- packaging opportunities
- positioning opportunities

It also produces a recommendation and business-impact assessment.

---

## Aggregator

Multiple analytical outputs should not automatically become an insight.

The Aggregator asks:

> **Do we have enough evidence to call this a meaningful business insight?**

It evaluates:

- meaningfulness
- confidence
- business impact
- evidence quality
- conflicts
- rationale
- recommendation

This creates the final decision point before delivery.

---

# 7. Confidence and Human-in-the-Loop

The system is designed around **selectivity**.

A consumer intelligence system that pushes every detected trend would quickly become another source of information overload.

The MVP therefore uses a confidence gate:

```text
                Aggregated Insight
                       │
                       ↓
              Evidence + Confidence
                       │
              ┌────────┼────────┐
              ↓        ↓        ↓
            HIGH     MEDIUM      LOW
              ↓        ↓        ↓
            Push      Review    Ignore
```

The current default thresholds are:

```text
Confidence >= 0.80  → High
Confidence >= 0.55  → Medium
Otherwise            → Low
```

There is also a minimum evidence-quality requirement.

A high model confidence score is **not sufficient** if evidence quality is below the configured threshold.

### Human-in-the-loop principle

> **AI accelerates intelligence; humans retain business decision authority.**

High-confidence insights can be delivered automatically through Slack.

Medium-confidence insights can be routed to a HITL webhook for review.

Low-confidence insights are not proactively pushed.

---

# 8. Data Model

The MVP uses PostgreSQL with pgvector.

```text
sources
   │
   └── signals
          │
          └── trends
                 │
                 └── insights
                        │
                        └── agent_events
```

### `sources`

Stores external observations.

Key information:

- source
- URL
- timestamp
- content
- source type
- credibility

### `signals`

Represents extracted market signals.

Key information:

- source
- topic
- entity
- timestamp
- embedding
- content hash

### `trends`

Represents detected patterns.

Key information:

- topic
- trend score
- growth rate
- first seen
- last seen

### `insights`

Stores the final business intelligence result.

Key information:

- India relevance
- business impact
- confidence
- recommendation
- status
- structured evidence

### `agent_events`

Provides execution-level observability.

It records:

- agent
- start/end time
- tokens
- cost
- status

This makes the system inspectable rather than treating the LLM as a black box.

---

# 9. Observability and Failure Design

The architecture treats reliability as part of the design.

For each insight, the system can retain the structured outputs used to reach the final recommendation.

The database also records agent execution events.

This makes it possible to investigate:

```text
Why was this insight generated?
        ↓
Which trend was selected?
        ↓
Which signals supported it?
        ↓
What did each agent conclude?
        ↓
What did the aggregator decide?
        ↓
Why did the confidence gate pass/fail?
```

The graph also records failed agent executions and marks an insight as failed if the overall graph execution fails.

---

# 10. Technology Choices

| Layer | Technology | Why |
|---|---|---|
| Application | Python | Simple, modular MVP implementation |
| Database | PostgreSQL | Persistent relational intelligence store |
| Vector storage | pgvector | Keeps vector search capability alongside application data |
| ORM | SQLAlchemy | Database abstraction |
| Migrations | Alembic | Reproducible schema changes |
| Orchestration | LangGraph | Explicit multi-step / fan-out-fan-in workflow |
| LLM | NVIDIA NIM | Structured LLM reasoning through an OpenAI-compatible API |
| Validation | Pydantic | Typed agent contracts |
| Embeddings | Sentence Transformers / NIM | Semantic representation of signals |
| Notifications | Slack + HITL webhook | Proactive delivery |
| Local infrastructure | Docker Compose | Reproducible PostgreSQL setup |

The important design choice is that **the framework follows the workflow**. LangGraph is used to make the analytical process explicit; PostgreSQL is used as the persistent source of truth; Pydantic makes agent outputs structured and machine-checkable.

---

# 11. Repository Structure

```text
.
├── app/
│   ├── agents/
│   │   ├── trend_agent.py
│   │   ├── consumer_agent.py
│   │   ├── ingredient_agent.py
│   │   ├── india_agent.py
│   │   ├── business_agent.py
│   │   ├── aggregator_agent.py
│   │   └── schemas.py
│   │
│   ├── collectors/
│   │   ├── rss.py
│   │   └── reddit.py
│   │
│   ├── confidence/
│   │   └── gate.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── ingestion/
│   ├── llm/
│   ├── notifications/
│   ├── orchestration/
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── events.py
│   │
│   ├── processing/
│   ├── prompts/
│   ├── signals/
│   ├── trends/
│   └── main.py
│
├── alembic/
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

The repository is organized around **responsibilities in the intelligence pipeline**, rather than around individual scripts.

---

# 12. Running the MVP

## Prerequisites

- Python 3.11+
- Docker
- NVIDIA NIM API access/model
- Internet access for RSS/Reddit collection

## 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

The Docker configuration exposes PostgreSQL on local port `5433`.

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -e .
```

## 4. Configure environment variables

Create a local `.env` file.

At minimum:

```env
DATABASE_URL=postgresql+psycopg://marketintel:marketintel@localhost:5433/marketintel

NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_API_KEY=your_nvidia_api_key
NIM_LLM_MODEL=your_available_nim_model
```

Optional embedding configuration:

```env
NIM_EMBEDDING_BASE_URL=
NIM_EMBEDDING_API_KEY=
NIM_EMBEDDING_MODEL=
```

If `NIM_EMBEDDING_MODEL` is left empty, the application uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

You can also configure RSS feeds and Reddit subreddits through:

```env
RSS_FEEDS=feed_url_1,feed_url_2
REDDIT_SUBREDDITS=FoodIndustry,india,IndianFood,HealthyFood
REDDIT_LIMIT=25
```

**Do not commit `.env` or API credentials to GitHub.**

## 5. Apply database migrations

```bash
alembic upgrade head
```

---

# 13. Running the Pipeline

The application exposes the following commands:

### Collect external sources

```bash
python -m app.main collect
```

Collects RSS and Reddit records, performs deduplication, and persists new sources.

### Extract signals

```bash
python -m app.main signals
```

Converts stored sources into market signals and generates embeddings.

### Detect trends

```bash
python -m app.main trends
```

Calculates and stores ranked candidate trends.

### Run only the Trend Agent

```bash
python -m app.main agent
```

Or run it for a specific trend:

```bash
python -m app.main agent 2
```

### Run the complete agent graph

```bash
python -m app.main graph
```

Or for a specific trend:

```bash
python -m app.main graph 2
```

### Run the complete end-to-end pipeline

```bash
python -m app.main all
```

This performs:

```text
Collect
  ↓
Signal extraction
  ↓
Trend detection
  ↓
Agentic analysis
  ↓
Confidence gate
  ↓
Notification / review
```

### Run continuously

```bash
python -m app.main schedule
```

The scheduler repeatedly executes the end-to-end pipeline using the configured interval.

---

# 14. What a Demo Should Show

The most useful demonstration is not a code walkthrough.

Show the **decision pipeline**.

### 1. Collection

```bash
python -m app.main collect
```

Show that new source records were persisted.

### 2. Signal generation

```bash
python -m app.main signals
```

Show examples of extracted market signals.

### 3. Trend detection

```bash
python -m app.main trends
```

Show the ranked candidate trends.

### 4. Agentic reasoning

```bash
python -m app.main graph <TREND_ID>
```

Show the graph progressing through:

```text
Trend
 ↓
Parallel specialist stage
 ↓
India relevance
 ↓
Business opportunity
 ↓
Aggregator
 ↓
Confidence gate
```

### 5. Final insight

The most important demo artifact is the stored `insights` record.

Show:

- detected trend
- India relevance
- business impact
- confidence
- recommendation
- evidence
- final status

The story should be:

> **Raw information → emerging pattern → India-specific interpretation → business recommendation → confidence-based action.**

---

# 15. Testing

Run the unit tests with:

```bash
pytest -q
```

The repository includes tests for:

- confidence-gate behaviour
- Pydantic agent output contracts

You can also verify that the application compiles:

```bash
python -m compileall -q app alembic tests
```

A full end-to-end run requires PostgreSQL, reachable source feeds, and valid NVIDIA NIM configuration.

---

# 16. Current MVP vs. Future System

The MVP intentionally proves the **closed intelligence loop** instead of attempting to build the complete production platform.

| Capability | Current MVP | Future |
|---|---:|---:|
| RSS ingestion | ✅ | |
| Reddit ingestion | ✅ | |
| PostgreSQL | ✅ | |
| pgvector embeddings | ✅ | |
| Signal extraction | ✅ | |
| Trend detection | ✅ | |
| LangGraph orchestration | ✅ | |
| Trend Agent | ✅ | |
| India Relevance Agent | ✅ | |
| Business Opportunity Agent | ✅ | |
| Evidence Aggregator | ✅ | |
| Confidence Gate | ✅ | |
| Slack delivery | ✅ | |
| HITL webhook | ✅ | |
| Consumer Agent | Interface / placeholder | 🔜 |
| Ingredient/Product Agent | Interface / placeholder | 🔜 |
| Search trends | | 🔜 |
| Product reviews | | 🔜 |
| Competitor intelligence | | 🔜 |
| More social platforms | | 🔜 |
| Real-time/event triggers | | 🔜 |
| Rich analyst dashboard | | 🔜 |
| Feedback learning | | 🔜 |

This distinction is intentional.

The MVP is designed to prove:

```text
Signal
  ↓
Trend
  ↓
India Relevance
  ↓
Business Opportunity
  ↓
Evidence
  ↓
Confidence
  ↓
Action
```

---

# 17. Design Principles

### 1. Start with the workflow, not the model

First understand what an analyst does. Then decide where AI can reduce the work.

### 2. Use agents for decisions

Each agent should represent a meaningful analytical responsibility.

### 3. Filter before reasoning

Do not send every raw signal to an expensive LLM.

```text
Many signals
    ↓
Cheap processing
    ↓
Candidate trends
    ↓
LLM reasoning
```

### 4. Evidence before action

An insight should retain the evidence and reasoning that produced it.

### 5. Confidence controls autonomy

Not every AI output deserves automatic delivery.

### 6. Humans retain business authority

The system recommends and prioritizes; it does not independently make irreversible business decisions.

### 7. Design for observability

An analyst should be able to understand why an insight was generated.

### 8. Build one complete loop before scaling

The first milestone is not "support every data source".

It is:

> **Collect → Detect → Localize → Recommend → Validate → Deliver.**

---

# 18. Roadmap

A production-oriented extension can evolve in four stages.

## Phase 1 — Data Foundation

- More reliable ingestion
- Better normalization
- Entity resolution
- Semantic deduplication
- More source types

## Phase 2 — Intelligence Layer

- Stronger topic clustering
- Temporal trend modelling
- Consumer behaviour signals
- Ingredient/product relationships
- Competitor intelligence

## Phase 3 — Agentic Reasoning

- Fully implemented Consumer Agent
- Fully implemented Ingredient/Product Agent
- Parallel specialist reasoning
- Better evidence aggregation
- Analyst feedback loops

## Phase 4 — Autonomous Intelligence Platform

```text
Continuous external signals
          ↓
Event / schedule triggers
          ↓
Signal processing
          ↓
Trend discovery
          ↓
Multi-agent reasoning
          ↓
India-specific intelligence
          ↓
Confidence + risk gate
          ↓
Human / business action
          ↓
Feedback
          ↺
```

The long-term objective is to create a reusable **consumer intelligence layer across multiple brands**, rather than a one-off market research application.

---

# 19. Final Takeaway

This project is fundamentally a **decision system**, not an LLM wrapper.

The architecture is built around one question:

> **How can we continuously transform a large and noisy external information space into a small number of high-value decisions for an Indian consumer business?**

The MVP demonstrates that loop:

```text
               INFORMATION OVERLOAD
                       ↓
                 DATA LAYER
                       ↓
                    SIGNALS
                       ↓
                    TRENDS
                       ↓
             SPECIALIST REASONING
                       ↓
               INDIA RELEVANCE
                       ↓
              BUSINESS OPPORTUNITY
                       ↓
              EVIDENCE + CONFIDENCE
                       ↓
                 ACTION / REVIEW
```

**The vision is not an AI that summarizes the market.**

**It is an autonomous intelligence layer that continuously identifies what is changing, understands why it matters to Indian consumers, and recommends what the business should do next.**
