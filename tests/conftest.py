import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

# override get_db
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    return TestClient(app)

import pytest
from tests.utils import register_and_login

@pytest.fixture
def auth_headers(client):
    token = register_and_login(client)
    return {
        "Authorization": f"Bearer {token}"
    }
