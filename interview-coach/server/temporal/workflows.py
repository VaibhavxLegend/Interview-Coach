from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import timedelta
from temporalio import workflow

# Types matching current API shapes
@dataclass
class AnswerRecord:
    question: str
    answer: str
    evaluation: Dict[str, Any]
    friendly: str
    embedding: Optional[List[float]] = None

@dataclass
class StartInput:
    session_id: int
    role: str
    seniority: str

@dataclass
class StepResult:
    current_question: Optional[str]
    last_record: Optional[AnswerRecord]
    status: str  # active|completed

@workflow.defn
class InterviewSessionWorkflow:
    def __init__(self) -> None:
        self._answers: List[AnswerRecord] = []
        self._status: str = "active"
        self._current_question: Optional[str] = None
        self._role: str = "general"
        self._seniority: str = "mid"
        self._session_id: int = 0

    @workflow.run
    async def run(self, args: StartInput) -> List[AnswerRecord]:
        self._role = args.role
        self._seniority = args.seniority
        self._session_id = args.session_id
        # initial question
        self._current_question = await workflow.execute_activity(
            "GenerateQuestion",
            self._role,
            self._seniority,
            start_to_close_timeout=timedelta(seconds=60),
        )
        # wait until session is completed via signal
        await workflow.wait_condition(lambda: self._status == "completed")
        return self._answers

    # Signal: submit answer for the current question
    @workflow.signal
    async def submit_answer(self, answer: str, transcript: Optional[str] = None) -> None:
        if self._status != "active" or not self._current_question:
            return
        question = self._current_question
        # evaluate and generate feedback
        evaluation: Dict[str, Any] = await workflow.execute_activity(
            "EvaluateAnswer",
            question,
            answer,
            start_to_close_timeout=timedelta(seconds=60),
        )
        friendly: str = await workflow.execute_activity(
            "GenerateFeedback",
            evaluation,
            start_to_close_timeout=timedelta(seconds=60),
        )
        embedding: Optional[List[float]] = await workflow.execute_activity(
            "EmbedText",
            answer,
            start_to_close_timeout=timedelta(seconds=30),
        )
        # persist atomically by activity
        await workflow.execute_activity(
            "PersistAnswerAndEvaluation",
            {
                "session_id": self._session_id,
                "question": question,
                "answer": answer,
                "transcript": transcript,
                "evaluation": evaluation,
                "friendly": friendly,
                "embedding": embedding,
            },
            start_to_close_timeout=timedelta(seconds=30),
        )
        record = AnswerRecord(question=question, answer=answer, evaluation=evaluation, friendly=friendly, embedding=embedding)
        self._answers.append(record)
        # next question
        self._current_question = await workflow.execute_activity(
            "GenerateQuestion",
            self._role,
            self._seniority,
            start_to_close_timeout=timedelta(seconds=60),
        )

    # Signal: end session; may include optional email
    @workflow.signal
    async def end_session(self, email: Optional[str] = None) -> None:
        self._status = "completed"
        # generate summary and optionally post webhook
        summary: str = await workflow.execute_activity(
            "GenerateSummary",
            [r.__dict__ for r in self._answers],
            start_to_close_timeout=timedelta(seconds=60),
        )
        if email:
            await workflow.execute_activity(
                "PostSummaryToWebhook",
                {
                    "session_id": self._session_id,
                    "email": email,
                    "summary": summary,
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

    # Query: current state snapshot
    @workflow.query
    def state(self) -> StepResult:
        return StepResult(current_question=self._current_question, last_record=(self._answers[-1] if self._answers else None), status=self._status)
