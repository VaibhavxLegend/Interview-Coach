from __future__ import annotations
from typing import Dict, Any
from .llm import llm_router
from .cache import get_redis


INTERVIEWER_SYSTEM = (
    "You are an expert interviewer. Ask one thoughtful interview question at a time based on the role and seniority."
)

EVALUATOR_SYSTEM = (
    "You are an expert evaluator. Score the candidate's answer on clarity, conciseness, confidence, and technical depth (0-10)."
    " Provide an overall score (0-10) and a brief bullet feedback and 2-3 concrete suggestions."
)

FEEDBACK_SYSTEM = (
    "You are a coach. Summarize strengths and areas to improve in a friendly tone. Give one short tip to improve next answer."
)


async def interviewer_agent(role: str, seniority: str) -> str:
    r = get_redis()
    key = f"questions:{role}:{seniority}"
    if r is not None:
        q = r.lpop(key)
        if q:
            return q
    # generate 3 and cache
    prompt = (
        f"Role: {role}\nSeniority: {seniority}\nGenerate 3 concise interview questions as a bullet list without numbering."
    )
    text = await llm_router.chat(prompt, system=INTERVIEWER_SYSTEM)
    lines = [ln.strip("- ") for ln in text.splitlines() if ln.strip()]
    questions = [ln for ln in lines if len(ln) > 10][:3] or [text.strip()]
    if r is not None and len(questions) > 1:
        # push remaining to cache
        for q in questions[1:]:
            r.rpush(key, q)
        r.expire(key, 3600)
    return questions[0]


async def evaluator_agent(question: str, answer: str) -> Dict[str, Any]:
    prompt = (
        "Evaluate the following answer to the interview question. Return JSON with keys: "
        "clarity, conciseness, confidence, technical_depth, overall, feedback, suggestions.\n\n"
        f"Question: {question}\nAnswer: {answer}\n"
        "Respond with ONLY valid JSON."
    )
    raw = await llm_router.chat(prompt, system=EVALUATOR_SYSTEM)
    import json
    try:
        data = json.loads(raw)
    except Exception:
        # simple rescue: wrap as feedback
        data = {
            "clarity": 5, "conciseness": 5, "confidence": 5, "technical_depth": 5, "overall": 5,
            "feedback": raw[:800], "suggestions": "Provide more structure and examples."
        }
    return data


async def feedback_agent(evaluation: Dict[str, Any]) -> str:
    prompt = (
        "Given the following evaluation, produce a short friendly summary with one actionable tip.\n\n"
        f"Evaluation: {evaluation}"
    )
    return await llm_router.chat(prompt, system=FEEDBACK_SYSTEM)
