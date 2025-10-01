from __future__ import annotations
from typing import Any, Optional
from .model import MockInterviewModel, SupportsPredict


class MLService:
    """Thin service layer around the ML model.

    Responsibilities:
    - Lazy-load or initialize the ML model
    - Provide a stable predict() interface
    - Hide implementation details from routers
    """

    _model: Optional[SupportsPredict] = None

    @classmethod
    def _load_model(cls) -> SupportsPredict:
        # TODO: Replace with real loading (e.g., from disk or remote endpoint)
        return MockInterviewModel()

    @classmethod
    def get_model(cls) -> SupportsPredict:
        if cls._model is None:
            cls._model = cls._load_model()
        return cls._model

    @classmethod
    def predict(cls, payload: dict[str, Any]) -> dict[str, Any]:
        model = cls.get_model()
        return model.predict(payload)
