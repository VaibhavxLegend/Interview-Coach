from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from ..ml.service import MLService


router = APIRouter()


class PredictIn(BaseModel):
    text: str | None = None
    answer: str | None = None


@router.post("/predict")
async def predict(body: PredictIn) -> dict[str, Any]:
    if not (body.text or body.answer):
        raise HTTPException(status_code=400, detail="Provide 'text' or 'answer'")
    payload = body.model_dump()
    result = MLService.predict(payload)
    return {"result": result}
