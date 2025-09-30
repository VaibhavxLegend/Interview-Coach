import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.anyio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
