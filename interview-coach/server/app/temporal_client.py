from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional
from temporalio.client import Client
from .config import settings

_client: Optional[Client] = None


async def get_client() -> Client:
    global _client
    if _client is None:
        _client = await Client.connect(settings.TEMPORAL_TARGET)
    return _client


async def start_interview_workflow(session_id: int, role: str, seniority: str) -> str:
    """Start workflow and return workflow_id."""
    from server.temporal.workflows import InterviewSessionWorkflow, StartInput

    client = await get_client()
    workflow_id = f"interview-session-{session_id}"
    handle = await client.start_workflow(
        InterviewSessionWorkflow.run,
        StartInput(session_id=session_id, role=role, seniority=seniority),
        id=workflow_id,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
    )
    return handle.id


async def signal_submit_answer(session_id: int, answer: str, transcript: Optional[str] = None) -> None:
    client = await get_client()
    workflow_id = f"interview-session-{session_id}"
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("submit_answer", answer, transcript)


async def signal_end_session(session_id: int, email: Optional[str]) -> None:
    client = await get_client()
    workflow_id = f"interview-session-{session_id}"
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("end_session", email)


async def query_state(session_id: int) -> Dict[str, Any]:
    client = await get_client()
    workflow_id = f"interview-session-{session_id}"
    handle = client.get_workflow_handle(workflow_id)
    return await handle.query("state")
