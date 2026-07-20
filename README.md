# OpsAgent (OpsPilot)

An enterprise-style **AIOps assistant** that combines:

- **RAG** over ops runbooks (TXT/PDF → chunk → embed → Chroma)
- A **ReAct agent** with monitoring tools (alerts / metrics / logs / topology)
- **Multi-turn memory** via LangGraph SQLite checkpointer (`thread_id` = conversation id)
- **Web search** when local knowledge is insufficient
- **Report generation** with prompt switching via middleware
- A **Streamlit** chat UI (OpsPilot) with persisted sidebar history

GitHub: https://github.com/62Kinsley/OpsAgent

---

## Features

| Area | What it does |
|------|----------------|
| Knowledge sync | Incremental Chroma indexing with MD5 fingerprinting (skip unchanged files, rebuild on edit, cleanup on delete) |
| RAG Q&A | Retrieve Top-K chunks and answer with a grounded prompt |
| Agent tools | Service/time context, alerts, metrics, logs, topology, aggregated reports, web search |
| Middleware | Log tool calls; switch `main_prompt` ↔ `report_prompt` after `fill_context_for_report` |
| Multi-turn | UI history in SQLite + agent memory via `SqliteSaver` (Scheme B: send only the new user message + `thread_id`) |
| UI | Multi-chat Streamlit app with sidebar history, suggested prompts, and light theme |

---

## Architecture

```text
User (Streamlit app.py)
        │
        ▼
   ReactAgent (LangChain create_agent)
        │
        ├── system prompt (main / report via middleware)
        ├── tools (RAG, observability mocks, web_search, report)
        ├── checkpointer (data/agent_checkpoints.db, keyed by thread_id)
        └── chat model (DashScope Qwen / optional Ollama)

UI chats (data/chat_history.db):
  conversation_id  →  message bubbles + sidebar titles
  same id used as  →  agent thread_id (memory isolation per chat)

Write path (indexing):
  data/*.txt|pdf  →  sync_service / vector_store.load_split_store()  →  chroma_db/

Read path (Q&A):
  query  →  retriever  →  qa_tool / QAService  →  LLM answer
```

**Read/write separation:** indexing is done by `rag/sync_service.py`; the agent and QA path only read from Chroma.

**Multi-turn (Scheme B):** each `run(query, thread_id=...)` sends only the latest user message. LangGraph reloads prior turns from the checkpointer for that `thread_id`.

---

## Tech Stack

- Python 3.11+
- LangChain / LangGraph (`create_agent` + middleware + `SqliteSaver`)
- ChromaDB + local HuggingFace embeddings (`BAAI/bge-small-zh-v1.5`)
- Chat: DashScope `ChatQwen` (default); optional Ollama via OpenAI-compatible API
- DuckDuckGo search (`ddgs`) for `web_search`
- Streamlit UI (`.streamlit/config.toml` forces light theme)

---

## Project Structure

```text
OpsAgent/
├── app.py                 # Streamlit UI entry
├── agent/
│   ├── react_agent.py     # Agent + SqliteSaver checkpointer
│   ├── tools.py           # Tools + mock observability data
│   └── middleware.py      # Logging + report prompt switch
├── rag/
│   ├── vector_store.py    # Incremental sync into Chroma
│   ├── qa_service.py      # Retrieve + answer
│   └── sync_service.py    # CLI/cron sync entry
├── model/factory.py       # Chat + embedding factories
├── prompts/               # main / report / RAG prompts
├── config/                # YAML configs
├── data/                  # Ops runbooks (+ local SQLite DBs, gitignored)
├── utils/
│   ├── chat_store.py      # UI conversation / message persistence
│   └── ...                # Config, paths, logging, loaders
└── .streamlit/config.toml # Light theme
```

---

## Setup

### 1. Clone and create a virtualenv

```bash
cd OpsAgent
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If Streamlit logs many `No module named 'torchvision'` warnings while watching `transformers`, install:

```bash
pip install torchvision
```

### 2. Environment variables

Create a `.env` in the project root:

```bash
DASHSCOPE_API_KEY=your_api_key_here
```

> Default chat path uses DashScope (`config/rag.yml`).  
> Embedding uses a **local** HuggingFace model (no DashScope embedding quota required).

### 3. Sync the knowledge base (first time)

From the project root:

```bash
python -m rag.sync_service
```

This loads files under `data/`, chunks them, embeds, and writes to `chroma_db/`.

Re-run after you add/edit/delete runbooks. Optional: schedule with cron every 10 minutes (see below).

---

## Usage

### Streamlit UI

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

If text looks white-on-white, use **⋯ → Settings → Theme → Light**, or rely on `.streamlit/config.toml` (restart Streamlit after changes).

### Demo prompts (English)

**Alert analysis**

```text
Please investigate today's alerts for the target service. Summarize the key symptoms, likely root cause, and recommended next actions.
```

**Multi-turn check (same chat)**

```text
Based on the previous analysis, what should we check first? Keep it short.
```

```text
What service were we discussing just now? Reply with only the service name.
```

**New-chat isolation**

Create **+ New chat**, then:

```text
What service were we discussing just now? If there is no prior conversation in this chat, reply exactly: NO_PRIOR_CONTEXT
```

Expected: `NO_PRIOR_CONTEXT`.

**Report mode**

```text
Generate today's ops daily report for the target service, including alerts, metrics, logs, and topology.
```

### Agent CLI smoke test

```bash
python -m agent.react_agent
```

### RAG QA only

```bash
python -m rag.qa_service
```

### Knowledge sync

```bash
python -m rag.sync_service
```

Optional cron (every 10 minutes):

```cron
*/10 * * * * cd /path/to/OpsAgent && /path/to/OpsAgent/.venv/bin/python -m rag.sync_service >> /path/to/OpsAgent/logs/sync.log 2>&1
```

---

## Configuration

| File | Purpose |
|------|---------|
| `config/rag.yml` | `chat_provider`, chat model name, API `base_url` |
| `config/chroma.yml` | Data path, chunk size, top_k, Chroma persist dir |
| `config/prompt.yml` | Paths to main / report / RAG prompt files |

### Chat provider (`config/rag.yml`)

**DashScope Qwen (default)**

```yaml
chat_provider: dashscope
chat_model_name: qwen3.7-plus
embedding_model_name: text-embedding-v1
base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

**Optional local Ollama**

```yaml
chat_provider: ollama
chat_model_name: qwen3.6
embedding_model_name: text-embedding-v1
base_url: http://localhost:11434/v1
```

Prompts live under `prompts/`:

- `main_prompt.txt` — default agent behavior
- `report_prompt.txt` — used after `fill_context_for_report` (middleware)
- `rag_qa_prompt.txt` — RAG answer generation

---

## Multi-turn design

| Layer | Store | Key | Responsibility |
|-------|--------|-----|----------------|
| UI history | `data/chat_history.db` (`utils/chat_store.py`) | `conversation_id` | Sidebar + chat bubbles |
| Agent memory | `data/agent_checkpoints.db` (LangGraph `SqliteSaver`) | `thread_id` (= same id) | Tool/model turns across invokes |

`app.py` calls:

```python
agent.run(prompt, thread_id=current_conversation_id)
```

Only the new user message is sent; prior turns come from the checkpointer.

---

## Agent Tools (summary)

| Tool | Role |
|------|------|
| `qa_tool` | Local runbook RAG |
| `web_search` | Public web search when local KB is insufficient |
| `get_target_service` / `get_time_range` | Demo context (randomized from lists) |
| `fetch_alert_data` / `fetch_metric_data` / `fetch_log_summary` / `fetch_topology_data` | Mock observability data |
| `fetch_report_data` | Aggregated report payload |
| `fill_context_for_report` | Signal for middleware to switch to report prompt |

> Observability tools currently use **in-memory mock data** for demos. Extend `generate_report_data()` later for Prometheus / Elasticsearch / alert platforms.

---

## Notes

- Prefer **local RAG** (`qa_tool`) before `web_search` (prompt + tool descriptions; soft rule).
- Mock alert/metric/log data covers a subset of services and time ranges (`last 1 hour`, `today`, `this month`). Random `get_time_range()` may hit empty results for ranges like `last 24 hours`.
- `get_target_service()` is **random** — the same prompt may analyze different services across runs; for multi-turn demos, follow up on the prior answer instead of repeating “target service”.
- Gitignored: `chroma_db/`, `md5.txt`, `.env`, `.venv/`, `data/chat_history.db`, `data/agent_checkpoints.db`, SQLite `-wal`/`-shm` files.

---

## License

Personal / educational project. Add a license file if you plan to redistribute.
