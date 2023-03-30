import asyncio
import httpx
import pytest
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from database.connection import Base, get_session, init_models, drop_models

load_dotenv()

DATABASE_URL_TEST: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/test'

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test

async def override_get_session() -> AsyncSession:
    async with async_session_test() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(autouse=True, scope='session')
async def init_db() -> None:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def default_client():
    async with httpx.AsyncClient(app=app, base_url='http://app') as client:
        yield client
