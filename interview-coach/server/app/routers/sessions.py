from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
import httpx
from ..config import settings
from ..models import Answer, Evaluation
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import InterviewSession
from ..agents import interviewer_agent
from ..config import settings
from typing import Optional
import asyncio

temporal_enabled = settings.ORCHESTRATOR.lower() == "temporal"
if temporal_enabled:
    try:
        from ..temporal_client import start_interview_workflow, signal_end_session, query_state
    except Exception:
        temporal_enabled = False


router = APIRouter()



@router.post("/start")
async def start_session(role: str = "software engineer", seniority: str = "mid", db: Session = Depends(get_db)):
    sess = InterviewSession(role=role, seniority=seniority, status="active")
    db.add(sess)
    db.commit()
    db.refresh(sess)
    # first question
    if temporal_enabled:
        await start_interview_workflow(sess.id, role, seniority)
        # poll state briefly to fetch the initial question
        question: Optional[str] = None
        for _ in range(10):
            st = await query_state(sess.id)
            question = st.get("current_question")
            if question:
                break
            await asyncio.sleep(0.3)
        return {"session_id": sess.id, "question": question or "Please provide your first answer when ready."}
    else:
        question = await interviewer_agent(role, seniority)
        return {"session_id": sess.id, "question": question}


class CompleteIn(BaseModel):
    email: EmailStr | None = None


@router.post("/{session_id}/complete")
async def complete_session(session_id: int, body: CompleteIn | None = None, db: Session = Depends(get_db)):
    sess = db.get(InterviewSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sess.status = "completed"
    sess.completed_at = datetime.utcnow()
    db.commit()
    # Create a brief summary from evaluations
    rows = db.execute(select(Answer, Evaluation).join(Evaluation, Evaluation.answer_id == Answer.id).where(Answer.session_id == session_id)).all()
    if rows:
        avg = lambda key: sum(getattr(ev, key) for _, ev in rows) / len(rows)
        summary = (
            f"Session {session_id} summary\n"
            f"Questions answered: {len(rows)}\n"
            f"Avg Clarity: {avg('clarity'):.1f}, Conciseness: {avg('conciseness'):.1f}, Confidence: {avg('confidence'):.1f}, Tech Depth: {avg('technical_depth'):.1f}, Overall: {avg('overall'):.1f}"
        )
    else:
        summary = f"Session {session_id} completed."

    if temporal_enabled:
        # Signal workflow to end session; workflow will handle webhook if configured
        await signal_end_session(session_id, body.email if body else None)
    else:
        # Optionally send via Power Automate webhook (LangGraph path only)
        if body and body.email and settings.POWER_AUTOMATE_WEBHOOK_URL:
            async with httpx.AsyncClient(timeout=20.0) as client:
                await client.post(settings.POWER_AUTOMATE_WEBHOOK_URL, json={"session_id": session_id, "email": body.email, "summary": summary})

    return {"status": "completed", "summary": summary}
