from __future__ import annotations
import os
from typing import Optional
from .config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

try:
    import anthropic
except Exception:
    anthropic = None  # type: ignore


class LLMRouter:
    def __init__(self) -> None:
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY and OpenAI else None
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY and anthropic else None
        self.local_endpoint = settings.LOCAL_LLAMA_ENDPOINT

    def has_any(self) -> bool:
        return bool(self.openai_client or self.anthropic_client or self.local_endpoint)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def chat(self, prompt: str, system: Optional[str] = None) -> str:
        # Try OpenAI
        if self.openai_client:
            try:
                resp = self.openai_client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system or "You are a helpful AI."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                )
                return resp.choices[0].message.content or ""
            except Exception:
                pass

        # Try Anthropic
        if self.anthropic_client:
            try:
                resp = self.anthropic_client.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                    max_tokens=800,
                    temperature=0.3,
                    system=system or "You are a helpful AI.",
                    messages=[{"role": "user", "content": prompt}],
                )
                # Join text outputs
                parts = []
                for block in resp.content:
                    if getattr(block, "type", None) == "text":
                        parts.append(getattr(block, "text", ""))
                return "\n".join(p for p in parts if p)
            except Exception:
                pass

        # Local fallback endpoint (OpenAI-compatible or simple /generate)
        if self.local_endpoint:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Try OpenAI-compatible /v1/chat/completions
                    try:
                        r = await client.post(
                            f"{self.local_endpoint.rstrip('/')}/v1/chat/completions",
                            json={
                                "model": os.getenv("LOCAL_MODEL", "llama3.1"),
                                "messages": [
                                    {"role": "system", "content": system or "You are a helpful AI."},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": 0.4,
                            },
                        )
                        if r.status_code == 200:
                            data = r.json()
                            return data["choices"][0]["message"]["content"]
                    except Exception:
                        pass

                    # Fallback generic /generate
                    r = await client.post(
                        f"{self.local_endpoint.rstrip('/')}/generate", json={"prompt": prompt}
                    )
                    r.raise_for_status()
                    return r.json().get("text", "")
            except Exception as e:
                raise RuntimeError(f"Local LLM call failed: {e}")

        raise RuntimeError("No LLM provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or LOCAL_LLAMA_ENDPOINT.")


llm_router = LLMRouter()
