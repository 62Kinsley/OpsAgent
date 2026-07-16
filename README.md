# OpsAgent (OpsPilot)

An enterprise-style **AIOps assistant** that combines:

- **RAG** over ops runbooks (TXT/PDF → chunk → embed → Chroma)
- A **ReAct agent** with monitoring tools (alerts / metrics / logs / topology)
- **Web search** when local knowledge is insufficient
- **Report generation** with prompt switching via middleware
- A **Streamlit** chat UI (OpsPilot)

GitHub: https://github.com/62Kinsley/OpsAgent

---

## Features

| Area | What it does |
|------|----------------|
| Knowledge sync | Incremental Chroma indexing with MD5 fingerprinting (skip unchanged files, rebuild on edit, cleanup on delete) |
| RAG Q&A | Retrieve Top-K chunks and answer with a grounded prompt |
| Agent tools | Service/time context, alerts, metrics, logs, topology, aggregated reports, web search |
| Middleware | Log tool calls; switch `main_prompt` ↔ `report_prompt` after `fill_context_for_report` |
| UI | Multi-chat Streamlit app with sidebar history and suggested prompts |

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
        └── chat model (DashScope-compatible API)

Write path (indexing):
  data/*.txt|pdf  →  sync_service / vector_store.load_split_store()  →  chroma_db/

Read path (Q&A):
  query  →  retriever  →  qa_tool / QAService  →  LLM answer
```

**Read/write separation:** indexing is done by `rag/sync_service.py`; the agent and QA path only read from Chroma.

---

## Tech Stack

- Python 3.11+
- LangChain / LangGraph (`create_agent` + middleware)
- ChromaDB + local HuggingFace embeddings (`BAAI/bge-small-zh-v1.5`)
- Chat model via DashScope OpenAI-compatible API (configurable in `config/rag.yml`)
- DuckDuckGo search (`ddgs`) for `web_search`
- Streamlit UI

---

## Project Structure

```text
OpsAgent/
├── app.py                 # Streamlit UI entry
├── agent/
│   ├── react_agent.py     # Agent assembly + run()
│   ├── tools.py           # Tools + mock observability data
│   └── middleware.py      # Logging + report prompt switch
├── rag/
│   ├── vector_store.py    # Incremental sync into Chroma
│   ├── qa_service.py      # Retrieve + answer
│   └── sync_service.py    # CLI/cron sync entry
├── model/factory.py       # Chat + embedding factories
├── prompts/               # main / report / RAG prompts
├── config/                # YAML configs
├── data/                  # Ops runbooks
└── utils/                 # Config, paths, logging, loaders
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

### 2. Environment variables

Create a `.env` in the project root:

```bash
DASHSCOPE_API_KEY=your_api_key_here
```

> Chat calls go through the DashScope-compatible endpoint configured in `config/rag.yml`.  
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

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

### Agent CLI smoke test

```bash
python -m agent.react_agent
```

Edit the `query` in `agent/react_agent.py` `__main__` as needed, e.g. report mode:

```text
Generate an operations report for order-service in the last 1 hour.
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
| `config/rag.yml` | Chat model name + API base URL |
| `config/chroma.yml` | Data path, chunk size, top_k, Chroma persist dir |
| `config/prompt.yml` | Paths to main / report / RAG prompt files |

Prompts live under `prompts/`:

- `main_prompt.txt` — default agent behavior
- `report_prompt.txt` — used after `fill_context_for_report` (middleware)
- `rag_qa_prompt.txt` — RAG answer generation

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

- Prefer **local RAG** (`qa_tool`) before `web_search` (enforced via prompt + tool descriptions; soft rule).
- Mock alert/metric/log data covers a subset of services and time ranges (`last 1 hour`, `today`, `this month`). Random `get_time_range()` may hit empty results for ranges like `last 24 hours`.
- `chroma_db/`, `md5.txt`, `.env`, and `.venv/` are gitignored.

---

## License

Personal / educational project. Add a license file if you plan to redistribute.
