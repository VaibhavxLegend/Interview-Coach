from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol


class SupportsPredict(Protocol):
    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class MockInterviewModel:
    """A placeholder ML model implementation.

    Replace this with a real model (e.g., a transformer loaded via
    Hugging Face, an on-disk sklearn model, or a remote endpoint).
    """

    name: str = "mock-interview-model"

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Echoes basic structure to keep contract stable
        text = payload.get("text") or payload.get("answer") or ""
        return {
            "model": self.name,
            "ok": True,
            "length": len(text),
            "summary": (text[:77] + "...") if len(text) > 80 else text,
        }
