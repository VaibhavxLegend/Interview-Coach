import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENV: str = os.getenv("ENV", "dev")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if origin.strip()
    ]

    # Postgres
    PGHOST = os.getenv("PGHOST", "localhost")
    PGPORT = int(os.getenv("PGPORT", "5432"))
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "postgres")
    PGDATABASE = os.getenv("PGDATABASE", "interview_coach")

    SQLALCHEMY_DATABASE_URI = (
        os.getenv(
            "DATABASE_URL",
            f"postgresql+psycopg://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}",
        )
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # LangSmith
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() in {"1", "true", "yes"}

    # LLMs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LOCAL_LLAMA_ENDPOINT = os.getenv("LOCAL_LLAMA_ENDPOINT")

    # Power Automate
    POWER_AUTOMATE_WEBHOOK_URL = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")

    # Orchestrator toggle
    ORCHESTRATOR = os.getenv("ORCHESTRATOR", "langgraph")  # langgraph|temporal
    TEMPORAL_TARGET = os.getenv("TEMPORAL_TARGET", "localhost:7233")
    TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "interview-coach")


settings = Settings()
