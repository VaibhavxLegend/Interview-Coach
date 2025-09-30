from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import select
from ..models import InterviewSession, Answer, Evaluation, IdealAnswer
from ..agents import interviewer_agent
from ..graph import run_interview_step
from ..embeddings import embed_text
from ..config import settings
import asyncio
temporal_enabled = settings.ORCHESTRATOR.lower() == "temporal"
if temporal_enabled:
    try:
        from ..temporal_client import signal_submit_answer, query_state
    except Exception:
        temporal_enabled = False


router = APIRouter()


class AnswerIn(BaseModel):
    question: str
    answer: str
    transcript: str | None = None


@router.post("/{session_id}/answer")
async def submit_answer(session_id: int, body: AnswerIn, db: Session = Depends(get_db)):
    sess = db.get(InterviewSession, session_id)
    if not sess or sess.status != "active":
        raise HTTPException(status_code=404, detail="Active session not found")

    if temporal_enabled:
        # Signal workflow to process the answer; persistence and evaluation happen in activities
        await signal_submit_answer(session_id, body.answer, body.transcript)
        # Poll state for latest record and next question
        record = None
        next_q = None
        for _ in range(20):
            st = await query_state(session_id)
            record = st.get("last_record")
            next_q = st.get("current_question")
            if record and next_q:
                break
            await asyncio.sleep(0.3)
        if not record:
            raise HTTPException(status_code=202, detail="Processing. Please retry momentarily.")
        ev = record.get("evaluation", {})
        friendly = record.get("friendly", "")
        return {
            "evaluation": {
                "clarity": float(ev.get("clarity", 5)),
                "conciseness": float(ev.get("conciseness", 5)),
                "confidence": float(ev.get("confidence", 5)),
                "technical_depth": float(ev.get("technical_depth", 5)),
                "overall": float(ev.get("overall", 5)),
                "feedback": str(ev.get("feedback", "")),
                "suggestions": str(ev.get("suggestions", "")),
                "friendly": friendly,
            },
            "next_question": next_q or await interviewer_agent(sess.role, sess.seniority),
        }
    else:
        # Persist answer
        ans = Answer(session_id=sess.id, question=body.question, content=body.answer, transcript=body.transcript)
        db.add(ans)
        db.commit()
        db.refresh(ans)

        # Embed for similarity search (future use)
        embedding = await embed_text(body.answer)
        ans.embedding = embedding
        db.add(ans)
        db.commit()

        # Evaluate via graph (includes feedback + next question)
        state = await run_interview_step(body.question, body.answer, sess.role, sess.seniority)
        ev = state["evaluation"]
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
        db.refresh(evaluation)

        friendly = state.get("friendly", "")
        next_q = state.get("next_question") or await interviewer_agent(sess.role, sess.seniority)

        return {
            "evaluation": {
                "clarity": evaluation.clarity,
                "conciseness": evaluation.conciseness,
                "confidence": evaluation.confidence,
                "technical_depth": evaluation.technical_depth,
                "overall": evaluation.overall,
                "feedback": evaluation.feedback,
                "suggestions": evaluation.suggestions,
                "friendly": friendly,
            },
            "next_question": next_q,
        }


class CompareIn(BaseModel):
    role: str
    seniority: str
    answer: str


@router.post("/compare")
async def compare_with_ideal(body: CompareIn, db: Session = Depends(get_db)):
    vec = await embed_text(body.answer)
    # Find nearest ideal answer
    # Using pgvector, similarity via cosine distance
    # SQLAlchemy 2.x with pgvector supports inner_product or l2_distance. We'll emulate cosine via inner_product on normalized vectors.
    # For simplicity, fetch top 5 and compute cosine manually.
    ideals = db.execute(
        select(IdealAnswer).where(IdealAnswer.role == body.role, IdealAnswer.seniority == body.seniority).limit(20)
    ).scalars().all()
    if not ideals:
        return {"matches": []}
    import numpy as np
    v = np.array(vec)
    v = v / (np.linalg.norm(v) + 1e-8)
    scored: list[tuple[float, IdealAnswer]] = []
    for ia in ideals:
        if ia.embedding:
            u = np.array(ia.embedding)
            u = u / (np.linalg.norm(u) + 1e-8)
            score = float(np.dot(u, v))  # cosine similarity
            scored.append((score, ia))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:3]
    return {"matches": [{"similarity": s, "answer": ia.answer} for s, ia in top]}
