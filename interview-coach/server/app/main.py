from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
import os
from .routers import sessions, qa, summary

app = FastAPI(title="Interview Coach API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Enable LangSmith tracing if configured
if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
