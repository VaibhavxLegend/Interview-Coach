from __future__ import annotations
from typing import Any, Dict, List, Optional
from temporalio import activity

# Adapters to existing helpers; these run in the worker process

@activity.defn(name="GenerateQuestion")
async def generate_question(role: str, seniority: str) -> str:
    # defer import to runtime to avoid circulars
    from server.app.agents import interviewer_agent
    return await interviewer_agent(role, seniority)

@activity.defn(name="EvaluateAnswer")
async def evaluate_answer(question: str, answer: str) -> Dict[str, Any]:
    from server.app.agents import evaluator_agent
    return await evaluator_agent(question, answer)

@activity.defn(name="GenerateFeedback")
async def generate_feedback(evaluation: Dict[str, Any]) -> str:
    from server.app.agents import feedback_agent
    return await feedback_agent(evaluation)

@activity.defn(name="EmbedText")
async def embed_text(answer: str) -> Optional[List[float]]:
    from server.app.embeddings import embed_text as do_embed
    return await do_embed(answer)

@activity.defn(name="PersistAnswerAndEvaluation")
async def persist_answer_and_evaluation(payload: Dict[str, Any]) -> None:
    # Persist using SQLAlchemy models
    from server.app.database import SessionLocal
    from server.app.models import Answer, Evaluation, InterviewSession

    session_id = int(payload["session_id"]) if isinstance(payload["session_id"], str) else payload["session_id"]
    with SessionLocal() as db:
        # ensure session exists
        sess = db.get(InterviewSession, session_id)
        if not sess:
            # skip if missing; in production we could create or raise
            return
        ans = Answer(
            session_id=session_id,
            question=payload["question"],
            content=payload["answer"],
            transcript=payload.get("transcript"),
            embedding=payload.get("embedding"),
        )
        db.add(ans)
        db.flush()
        ev = payload["evaluation"]
        evaluation = Evaluation(
            answer_id=ans.id,
            clarity=float(ev.get("clarity", 5)),
            conciseness=float(ev.get("conciseness", 5)),
            confidence=float(ev.get("confidence", 5)),
            technical_depth=float(ev.get("technical_depth", 5)),
            overall=float(ev.get("overall", 5)),
            feedback=str(ev.get("feedback", "")),
            suggestions=str(ev.get("suggestions", "")),
        )
        db.add(evaluation)
        db.commit()

@activity.defn(name="GenerateSummary")
async def generate_summary(records: List[Dict[str, Any]]) -> str:
    # very simple textual summary; can be replaced with LLM later
    if not records:
        return "No answers submitted."
    overall = [float(r.get("evaluation", {}).get("overall", 0)) for r in records]
    avg = sum(overall) / max(1, len(overall))
    return f"Total answers: {len(records)}. Average overall score: {avg:.1f}."

@activity.defn(name="PostSummaryToWebhook")
async def post_summary_to_webhook(payload: Dict[str, Any]) -> None:
    # reuse existing summary endpoint (if needed) or post directly to Power Automate
    import os
    import httpx
    url = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")
    if not url:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=payload)
