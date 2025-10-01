from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from ..coach_agent import (
    generate_questions,
    pick_question,
    generate_feedback_with_ollama,
    evaluate_feedback,
)


router = APIRouter()


class FeedbackIn(BaseModel):
    question: str | None = None
    response: str
    num_questions: int | None = 5


@router.post("/feedback")
async def feedback(body: FeedbackIn) -> dict[str, Any]:
    try:
        question = body.question or pick_question(generate_questions(body.num_questions or 5))
        feedback_text = generate_feedback_with_ollama(question, body.response)
        eval_result = evaluate_feedback(question, feedback_text)
        return {
            "question": question,
            "feedback": feedback_text,
            "evaluation": eval_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
