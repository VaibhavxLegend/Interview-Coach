from __future__ import annotations
import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker

from .workflows import InterviewSessionWorkflow
from . import activities as activity_module


async def run_worker() -> None:
    target = os.getenv("TEMPORAL_TARGET", "localhost:7233")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "interview-coach")
    client = await Client.connect(target)
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[InterviewSessionWorkflow],
        activities=[
            activity_module.generate_question,
            activity_module.evaluate_answer,
            activity_module.generate_feedback,
            activity_module.embed_text,
            activity_module.persist_answer_and_evaluation,
            activity_module.generate_summary,
            activity_module.post_summary_to_webhook,
        ],
    )
    print(f"Worker started on {target} queue={task_queue}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
