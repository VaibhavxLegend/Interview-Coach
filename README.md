# Interview Coach — Mock interview with AI agents

Full‑stack app where users practice mock interviews, answer by typing or voice, and an agentic workflow evaluates responses (clarity, conciseness, confidence, tech depth), stores results, and suggests improvements. Includes summary email via Power Automate.

## Tech stack

- Frontend: Next.js (App Router), TailwindCSS v4
- Backend: FastAPI
- Agents: LangGraph (Interviewer → Evaluator → Feedback), OpenAI/Anthropic with local fallback
- Data: Postgres + pgvector (embeddings), Redis (question cache)
- Ops: Docker Compose for dev (DB + Redis)

## Quickstart (Windows cmd)

1. Start DB + Redis (optional but recommended)

   ```cmd
   docker compose up -d db redis
   ```

2. Install frontend deps and run Next.js

   ```cmd
   npm install
   npm run dev
   ```

3. Create a Python venv, install backend deps, and run API (port 8000)

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r server\requirements.txt
   set PORT=8000
   uvicorn app.main:app --app-dir server --host 0.0.0.0 --port 8000
   ```

4. Initialize database (optional seed)

   ```cmd
   python -c "from app.init_db import init; init()" --app-dir server
   ```

Open <http://localhost:3000>. The app will call the API at <http://localhost:8000> by default. Change `NEXT_PUBLIC_API_BASE` if needed.

## Environment variables

- Backend (.env)
  - DATABASE_URL or PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE
  - REDIS_URL
  - OPENAI_API_KEY / ANTHROPIC_API_KEY (optional)
  - LOCAL_LLAMA_ENDPOINT (optional fallback)
  - LANGSMITH_API_KEY, LANGSMITH_TRACING=true (optional tracing)
  - POWER_AUTOMATE_WEBHOOK_URL (optional emails)
  - ORCHESTRATOR (langgraph|temporal), TEMPORAL_TARGET, TEMPORAL_TASK_QUEUE
- Frontend (.env.local)
  - NEXT_PUBLIC_API_BASE=<http://localhost:8000>

## API overview

- POST /api/sessions/start → { session_id, question }
- POST /api/qa/{session_id}/answer → evaluation + next_question
- POST /api/sessions/{session_id}/complete { email? } → { summary }
- POST /api/summary/send { session_id, email, summary } → posts to Power Automate
- POST /api/qa/compare { role, seniority, answer } → matches to ideal answers (pgvector)

## Notes on LLMs and fallback

By default the app will try OpenAI first, then Anthropic, then an optional local LLM endpoint. Set one of:

- OPENAI_API_KEY and optional OPENAI_MODEL
- ANTHROPIC_API_KEY and optional ANTHROPIC_MODEL
- LOCAL_LLAMA_ENDPOINT (supports OpenAI‑compatible /v1/chat/completions or /generate)

## Temporal orchestration (optional)

You can use Temporal instead of the in‑process LangGraph flow.

Toggle via backend env:

- ORCHESTRATOR=temporal (default is `langgraph`)
- TEMPORAL_TARGET=localhost:7233
- TEMPORAL_TASK_QUEUE=interview-coach

Worker Quickstart (Windows cmd):

```cmd
docker run --name temporal -d -p 7233:7233 temporalio/auto-setup:1.24
pip install -r server/requirements.txt
set TEMPORAL_TARGET=localhost:7233
set TEMPORAL_TASK_QUEUE=interview-coach
python -m server.temporal.worker
```

See `docs/temporal.md` for the workflow design and details.

## Dev tips

- Seed a couple ideal answers: `python -c "from app.init_db import init; init()"` (in server context)
- Health check: GET <http://localhost:8000/api/health>
- Update `.env` and `.env.local` to point API/DB anywhere you like.
