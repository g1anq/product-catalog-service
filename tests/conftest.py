import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    # Sử dụng TestClient một cách đồng bộ để tránh xung đột loop với asyncpg
    with TestClient(app) as c:
        yield c