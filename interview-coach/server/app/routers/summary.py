from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..config import settings
import httpx


router = APIRouter()


class SummaryPayload(BaseModel):
    session_id: int
    email: EmailStr
    summary: str


@router.post("/send")
async def send_summary(body: SummaryPayload):
    if not settings.POWER_AUTOMATE_WEBHOOK_URL:
        raise HTTPException(status_code=400, detail="POWER_AUTOMATE_WEBHOOK_URL not configured")

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(settings.POWER_AUTOMATE_WEBHOOK_URL, json=body.model_dump())
        if r.status_code >= 300:
            raise HTTPException(status_code=502, detail=f"Failed to post to Power Automate: {r.text}")
    return {"status": "sent"}
