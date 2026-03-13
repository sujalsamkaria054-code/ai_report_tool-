# AI Report Tool

A scaffolded AI reporting system with a modular backend orchestration pipeline and a frontend chat UI.

## Architecture Overview

The system follows this high-level flow:

1. **User input** (query + optional uploaded document)
2. **Router Agent** classifies request (`rag_only`, `analysis_only`, `chart_only`, `report_only`, `hybrid`)
3. **Tool chain execution** (as needed):
   - RAG Agent
   - Data Analysis Agent
   - Chart Agent
   - Report Agent
4. **Formatter Agent** builds a final frontend-safe structured response
5. **Frontend** renders content, charts, tables, and report sections separately

### Backend orchestration path

`User -> Router -> (RAG/Analysis/Chart/Report) -> Formatter -> APIResponse`

The orchestrator lives in `backend/app/graph/graph.py` and uses route transitions defined in `backend/app/graph/routes.py`.

---

## Folder Explanation

```text
project/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app (/health, /upload, /query)
│   │   ├── config.py               # App settings
│   │   ├── graph/                  # Orchestration graph + routes + state
│   │   ├── agents/                 # Router/RAG/Analysis/Chart/Report/Formatter agents
│   │   ├── services/               # PDF, vector store, retriever, dataframe, chart, report
│   │   ├── ingestion/              # PDF/text/table extraction, chunking, embeddings
│   │   ├── schemas/                # Pydantic schemas for route/chart/table/report/response
│   │   ├── prompts/                # Prompt templates per stage
│   │   └── utils/                  # Logger, validators, helpers
│   └── requirements.txt            # Backend dependencies
├── frontend/
│   ├── app/page.tsx                # Main page
│   ├── components/
│   │   ├── chat/                   # Chat window, input, message card
│   │   ├── charts/                 # Chart renderer + bar/line/pie components
│   │   ├── report/                 # Structured report display components
│   │   └── tables/                 # Structured data table renderer
│   └── lib/
│       ├── api.ts                  # Typed API helper functions
│       └── types.ts                # Shared frontend types mirroring backend schema
└── README.md
```

---

## How to Run Backend

From repository root:

```bash
cd project/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend endpoints:

- `GET /health`
- `POST /upload`
- `POST /query`

---

## How to Run Frontend

> Note: this scaffold currently includes frontend source files but may not include full Next.js project config (`package.json`, `tsconfig.json`, etc.) in this repository state.

If/when full Next.js config is present:

```bash
cd project/frontend
npm install
npm run dev
```

Default dev URL:

- `http://localhost:3000`

---

## Supported Flows

### 1) Summary query on uploaded PDF

- Upload document via `/upload`
- Send query with returned `document_id`
- Router usually selects `rag_only`
- RAG retrieves relevant chunks and formatter returns structured response

### 2) Chart query on extracted table data

- Upload a document containing table-like data
- Query for chart/graph/visualization
- Router selects `chart_only` (or `hybrid`)
- Analysis + chart generation run; charts returned in `charts` field

### 3) Full report with charts

- Query includes report + chart intent
- Router selects `hybrid`
- RAG + analysis + chart + report run
- Formatter returns content + report + charts + tables + sources

### 4) Missing table data fallback

- Analysis returns deterministic `no_data`
- Chart stage returns empty list gracefully
- Response still valid and structured

### 5) Missing retrieval results fallback

- RAG returns explicit no-context fallback text
- Response stays schema-compliant and user-facing

---

## Example API Responses

### `GET /health`

```json
{
  "status": "ok"
}
```

### `POST /upload` response

```json
{
  "document_id": "f3f2f7d1c2b44e62b2d0a9f0426a1234",
  "filename": "quarterly_report.pdf",
  "content_type": "application/pdf",
  "size_bytes": 128034,
  "status": "uploaded"
}
```

### `POST /query` request

```json
{
  "query": "Create a report with charts for Q2 performance",
  "document_id": "f3f2f7d1c2b44e62b2d0a9f0426a1234"
}
```

### `POST /query` response (structured)

```json
{
  "content": "Your report is ready. Included 2 chart(s), 1 table(s), and 2 source reference(s).",
  "report": {
    "title": "Analysis Report: Create a report with charts for Q2 performance",
    "summary": "...",
    "insights": [
      "Trend insight (sales): revenue: increasing"
    ],
    "recommendations": [
      "Review the detected trends and validate them against recent operational context."
    ],
    "conclusion": "The report combines retrieval context and deterministic data analysis for actionable decision support."
  },
  "charts": [
    {
      "chart_type": "line",
      "title": "sales_by_month - revenue_sum",
      "x_axis": ["Jan", "Feb", "Mar"],
      "series": [{ "name": "revenue_sum", "values": [10, 15, 22] }],
      "labels": [],
      "values": [],
      "meta": { "group_by": "month", "metric": "revenue_sum" }
    }
  ],
  "tables": [
    {
      "name": "sales",
      "columns": ["month", "revenue"],
      "rows": [
        { "month": "Jan", "revenue": 10 },
        { "month": "Feb", "revenue": 15 }
      ]
    }
  ],
  "sources": [
    "document://f3f2f7d1c2b44e62b2d0a9f0426a1234",
    "project/backend/uploads/f3f2f7d1c2b44e62b2d0a9f0426a1234_quarterly_report.pdf"
  ]
}
```

---

## Notes

- This is a scaffold designed for deterministic local development.
- Replaceable extension points include:
  - vector backend (Chroma/FAISS/Pinecone/Supabase)
  - embedding model
  - LLM generation
  - robust PDF/table extraction
- Response formatting keeps `content`, `report`, `charts`, `tables`, and `sources` separated for frontend safety.


---

## Environment Setup

1. Copy root example file:

```bash
cp .env.example .env
```

2. Fill in required provider keys in `.env`.

### Required API keys by provider

- **Groq**
  - `GROQ_API_KEY`
- **Hugging Face**
  - `HUGGINGFACE_API_KEY` (optional for some local paths, recommended for hosted usage)
- **Supabase**
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY` and/or `SUPABASE_SERVICE_ROLE_KEY`

> Security note: keep all backend secrets on the backend only. Frontend should only use `NEXT_PUBLIC_API_BASE_URL`.

### Provider roles in this architecture

- **Groq**: chat completion/model responses (LLM stage)
- **Hugging Face**: embedding model for chunk vectors
- **Supabase**: document/chunk storage + vector similarity retrieval backend

Current code provides provider-ready scaffolding and safe runtime checks via `/config-status`.

---

## Supabase Setup Guidance

Recommended schema: `public` (configurable via `SUPABASE_DB_SCHEMA`).

### Table: `documents`

Suggested columns:

- `id uuid primary key default gen_random_uuid()`
- `file_name text not null`
- `file_type text`
- `title text`
- `storage_path text`
- `metadata jsonb default '{}'::jsonb`
- `created_at timestamptz default now()`

### Table: `document_chunks`

Suggested columns:

- `id uuid primary key default gen_random_uuid()`
- `document_id uuid references documents(id) on delete cascade`
- `chunk_index int not null`
- `content text not null`
- `embedding vector(384)`
- `metadata jsonb default '{}'::jsonb`
- `created_at timestamptz default now()`

### Recommended indexes

- Vector index on `embedding` (`ivfflat` or `hnsw`, depending on pgvector/Postgres version)
- B-tree index on `document_id`

### Embedding dimension note

`sentence-transformers/all-MiniLM-L6-v2` uses **384** dimensions. If you switch embedding models, update:

- Supabase `embedding vector(<new_dim>)`
- `EMBEDDING_DIMENSION` in configuration

---

## Supabase RPC Function Shape

Recommended RPC function: `match_document_chunks`

Suggested signature:

- `query_embedding vector`
- `match_count int`
- `document_filter uuid default null` (optional)

Purpose:

- return nearest chunks by vector similarity
- optionally constrain to a specific document

The codebase currently scaffolds this function name in configuration (`SUPABASE_MATCH_FUNCTION`) for later full implementation.

---

## Configuration Status Endpoint

`GET /config-status` returns safe provider readiness without exposing secrets, for example:

```json
{
  "groq_configured": true,
  "huggingface_configured": true,
  "supabase_configured": true,
  "model": "llama-3.3-70b-versatile",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "issues": []
}
```
