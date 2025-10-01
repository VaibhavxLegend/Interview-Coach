from __future__ import annotations

import random
from typing import Any, Optional

from .config import settings

# LangChain / Ollama model
try:
    from langchain_community.chat_models import ChatOllama  # type: ignore
    from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency handling
    ChatOllama = None  # type: ignore
    HumanMessage = None  # type: ignore
    SystemMessage = None  # type: ignore
    _import_error = e
else:
    _import_error = None


# Judgeval (optional)
try:
    from judgeval import JudgmentClient  # type: ignore
    from judgeval.data import Example  # type: ignore
    from judgeval.scorers import AnswerRelevancyScorer  # type: ignore
    from judgeval.common.tracer import Tracer  # type: ignore
    from judgeval.integrations.langgraph import JudgevalCallbackHandler  # type: ignore
except Exception:
    JudgmentClient = None  # type: ignore
    Example = None  # type: ignore
    AnswerRelevancyScorer = None  # type: ignore
    Tracer = None  # type: ignore
    JudgevalCallbackHandler = None  # type: ignore


def _get_chat_model():
    """Create the Ollama chat model using env-configured name.

    Falls back to 'llama3' if LOCAL_MODEL is not set.
    """
    if ChatOllama is None:
        raise RuntimeError(
            f"langchain-community not available: {_import_error}. Install 'langchain-community' to enable ChatOllama."
        )
    model_name = settings.LOCAL_MODEL or "llama3"
    return ChatOllama(model=model_name)


def generate_questions(num_questions: int = 3) -> list[str]:
    chat_model = _get_chat_model()
    system_message = SystemMessage(
        content=(
            "\n    You are an expert interview coach. Please generate a list of diverse behavioral interview questions "
            "that help evaluate a candidate’s experience, problem-solving, teamwork, and leadership skills. "
            "Only return a numbered list.\n    "
        )
    )
    user_message = HumanMessage(content=f"\n    Generate {num_questions} behavioral interview questions.\n    ")
    response = chat_model.invoke([system_message, user_message])
    lines = str(response.content).strip().split("\n")
    questions = [line.split(".", 1)[1].strip() for line in lines if "." in line]
    # If parsing fails (no numbering), just return the lines as-is up to num_questions
    if not questions:
        questions = [l.strip("-• ") for l in lines if l.strip()][:num_questions]
    return questions


def pick_question(questions: list[str]) -> str:
    return random.choice(questions)


def generate_feedback_with_ollama(question: str, user_response: str) -> str:
    chat_model = _get_chat_model()
    system_message = SystemMessage(
        content=(
            "\n    You are a career coaching expert. Your task is to give clear, detailed feedback on behavioral interview answers.\n"
            "    Evaluate whether the answer follows the STAR (Situation, Task, Action, Result) method, uses strong action words, and is well-structured.\n"
            "    Provide actionable advice on how to improve.\n    "
        )
    )
    user_message = HumanMessage(
        content=(
            f"\n    Interview Question: {question}\n    Candidate's Response: {user_response}\n\n    Please provide detailed feedback.\n    "
        )
    )
    response = chat_model.invoke([system_message, user_message])
    return str(response.content)


def evaluate_feedback(question: str, feedback: str) -> dict[str, Any]:
    """Evaluate the feedback with judgeval if available; otherwise return warnings.

    Returns a dict with keys: available(bool), warnings(list[str]), result(Any|None)
    """
    warnings: list[str] = []
    if "STAR" not in feedback.upper():
        warnings.append("Feedback does not mention STAR method.")
    if len(feedback.split()) < 50:
        warnings.append("Feedback may be too short.")

    if not (JudgmentClient and Example and AnswerRelevancyScorer):
        return {"available": False, "warnings": warnings, "result": None}

    client = JudgmentClient()
    example = Example(
        input=question,
        actual_output=feedback,
        retrieval_context=[
            "Good feedback on behavioral answers should mention structure, clarity, use of STAR method, and action words."
        ],
    )
    scorer = AnswerRelevancyScorer(threshold=0.5)
    result = client.run_evaluation(
        examples=[example],
        scorers=[scorer],
        model="gpt-4o",
        project_name="interview-coach-agent",
    )
    return {"available": True, "warnings": warnings, "result": result}


def run_agent(callbacks: Optional[list[Any]] = None) -> None:  # pragma: no cover - CLI helper
    questions = generate_questions(num_questions=5)
    question = pick_question(questions)
    print(f"\n📝 Interview Question:\n➡️ {question}")
    user_response = input("\nYour Response:\n> ")

    feedback = generate_feedback_with_ollama(question, user_response)
    print("\n🗒️ AI-Generated Feedback:")
    print(feedback)

    eval_result = evaluate_feedback(question, feedback)
    print("\n🎯 Judgeval Evaluation Result:")
    print(eval_result.get("result"))


__all__ = [
    "generate_questions",
    "pick_question",
    "generate_feedback_with_ollama",
    "evaluate_feedback",
    "run_agent",
]
