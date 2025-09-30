from __future__ import annotations
import os
import numpy as np
from .config import settings

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


async def embed_text(text: str) -> list[float]:
    if settings.OPENAI_API_KEY and OpenAI:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            resp = client.embeddings.create(model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"), input=text)
            return list(map(float, resp.data[0].embedding))
        except Exception:
            pass
    # Fallback: simple hash-based pseudo embedding (fixed dim 1536)
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.normal(size=1536).astype(np.float32)
    vec = vec / (np.linalg.norm(vec) + 1e-8)
    return vec.tolist()
