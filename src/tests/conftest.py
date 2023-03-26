import asyncio
import httpx
import pytest
from main import app
from database.connection import init_models, drop_models

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

async def init_db():
    await init_models(env='test')

async def drop_db():
    await drop_models(env='test')

@pytest.fixture(scope='session')
async def default_client():
    await init_db()
    async with httpx.AsyncClient(app=app, base_url='http://app') as client:
        yield client
        await drop_db()
