import asyncio
import httpx
import pytest
from main import app
from database.connection import Settings

test_settings = Settings(env='test')

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
async def default_client():
    await test_settings.init_models()
    async with httpx.AsyncClient(app=app, base_url='http://app') as client:
        yield client
        await test_settings.drop_models()
