# Temporal orchestration plan

This document outlines how to migrate the existing LangGraph-based in-process orchestration to a Temporal workflow while preserving behavior and adding reliability, retries, and visibility.

## Goals

- Model the interview lifecycle as a durable workflow
- Keep side effects (LLM calls, DB writes, Redis ops, webhook calls) in Activities with retries
- Make the UI interact with a Workflow via signals/queries (for live runs) or continue with REST while the backend delegates to Workflow

## Proposed architecture overview

Workflow: `InterviewWorkflow`

This document outlines how to migrate the existing LangGraph-based in-process orchestration to a Temporal workflow while preserving behavior and adding reliability, retries, and visibility.

## Objectives

- Model the interview lifecycle as a durable workflow
- Keep side effects (LLM calls, DB writes, Redis ops, webhook calls) in Activities with retries
- Make the UI interact with a Workflow via signals/queries (for live runs) or continue with REST while the backend delegates to Workflow

## Proposed architecture

Workflow: `InterviewWorkflow`

- State (minimal):
  - sessionId: int
  - role: string
  - seniority: string
  - status: "active" | "completed"
  - currentQuestion: string | null
  - answers: Array<{ question: string; answer: string; evaluation: Scores | null }>
  - summary: string | null

- Activities:
  1) `GenerateQuestion(role, seniority) -> string`
     - Uses Redis cache and LLM (same as current `interviewer_agent`)
  2) `EvaluateAnswer(question, answer) -> Evaluation`
     - Uses LLM (same as current `evaluator_agent`) and parses JSON
  3) `GenerateFeedback(evaluation) -> string`
     - Uses LLM (same as current `feedback_agent`)
  4) `PersistAnswerAndEvaluation(sessionId, answerRecord)` -> void
     - Writes Answer + Evaluation + Embedding to Postgres/pgvector
  5) `PostSummaryToWebhook(sessionId, email, summary)` -> void
     - Posts to Power Automate if configured
  6) `EmbedText(text) -> float[1536]`
     - Calls OpenAI embeddings (or fallback) used by Persist activity

- Signals (from UI or backend):
  - `SubmitAnswer(answer: string)`
  - `EndSession(email?: string)`

- Queries (from UI/backend):
  - `GetStatus()` -> { status, currentQuestion, lastEvaluation?, summary? }
  - `GetSession()` -> full state view (optional)

## Workflow execution outline

```mermaid
Start(sessionId, role, seniority)
  currentQuestion = GenerateQuestion(role, seniority)
  loop while status == active
    wait for one of:
      - SubmitAnswer(answer)
         evaluation = EvaluateAnswer(currentQuestion, answer)
         feedback = GenerateFeedback(evaluation)
         PersistAnswerAndEvaluation(sessionId, {question, answer, evaluation, feedback, embedding})
         currentQuestion = GenerateQuestion(role, seniority)
         update workflow state (answers[], currentQuestion)
      - EndSession(email?)
         status = completed
         summary = summarize answers/evaluations (optionally a small activity)
         if email provided: PostSummaryToWebhook(sessionId, email, summary)
         exit loop
```

Notes:

- Summary can be produced by an activity `GenerateSummary(answers) -> string` or computed in workflow code (no side effects).
- Activities should be idempotent (e.g., Persist with an idempotency key: sessionId + answer index).

## Retries and timeouts

Per-activity recommended defaults (tune as needed):

- `GenerateQuestion` / `EvaluateAnswer` / `GenerateFeedback`: retry 3–5 times, exponential backoff, 30–60s schedule-to-close
- `PersistAnswerAndEvaluation`: retry on transient DB errors, backoff, 10–20s timeouts
- `PostSummaryToWebhook`: retry 3 times, backoff, 10s timeout
- `EmbedText`: retry 3 times, 15–30s

## Data contracts

```ts
type Scores = {
  clarity: number;        // 0..10
  conciseness: number;    // 0..10
  confidence: number;     // 0..10
  technical_depth: number;// 0..10
  overall: number;        // 0..10
  feedback: string;
  suggestions: string;
};

type AnswerRecord = {
  question: string;
  answer: string;
  evaluation: Scores;
  friendly: string;       // coach summary
  embedding?: number[];   // 1536 floats
};
```

## Security & observability

- Secrets: use environment variables or a secrets manager; activities read from process env
- Observability: keep LangSmith tracing for LLM calls; use Temporal Web UI for workflow/activities

## Migration strategy

1) "Sidecar" design: keep the REST endpoints; inside handlers, start or signal a Temporal workflow (e.g., `start_session`, `submit_answer`, `complete_session`)
2) Move existing agent calls into activities without changing prompts
3) Gradually shift frontend to use Temporal queries/signals directly (optional) while maintaining REST fallback
4) Roll out streaming UX later via Temporal signals or SSE from the API

## Local development

- Temporal server: `temporal server start-dev`
- Add Python SDK dependency (proposal): `temporalio`
- Create a worker service (e.g., `server/worker.py`) to register activities and workflows
- Configure task queues (e.g., `interview-task-queue`) and run the worker alongside the API

---

## Quickstart: run Temporal worker locally

Prerequisites:

- Temporal server running locally. You can use the Docker image `temporalio/auto-setup` or `temporal server start-dev` if you have the CLI.
- Python dependencies installed in the backend env (includes `temporalio`).

Steps (Windows cmd):

```cmd
REM 1) Start Temporal server via Docker (example)
docker run --name temporal -d -p 7233:7233 temporalio/auto-setup:1.24

REM 2) Install backend deps (from repo root)
pip install -r server/requirements.txt

REM 3) Run the worker from repo root
set TEMPORAL_TARGET=localhost:7233
set TEMPORAL_TASK_QUEUE=interview-coach
python -m server.temporal.worker
```

Environment variables:

- TEMPORAL_TARGET: host:port for Temporal (default localhost:7233)
- TEMPORAL_TASK_QUEUE: task queue name (default interview-coach)

Integration approach:

- Keep existing REST endpoints. Over time, route session start to start a workflow and subsequent answers to send a signal, and query for state.

### Orchestrator toggle

Set `ORCHESTRATOR=temporal` in your environment to route API requests through the Temporal workflow (start, submit, complete). Defaults to `langgraph` which uses the in-process LangGraph flow.

