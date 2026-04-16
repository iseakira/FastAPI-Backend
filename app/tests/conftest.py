from httpx import ASGITransport, AsyncClient
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture(scope="module")
async def client():
  async with AsyncClient(
    app=app,
    transport=ASGITransport(app),
    base_url="http://test",
  ) as client:
    yield client
