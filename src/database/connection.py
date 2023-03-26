from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY: str = os.getenv('SECRET_KEY')

Base = declarative_base()

def get_engine(env: str = 'postgres'):
    DATABASE_URL: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/{env}'
    engine = create_async_engine(DATABASE_URL, echo=True)
    return engine

def create_session():
    async_session = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return async_session()

async def init_models(env: str = 'postgres') -> None:
    async with get_engine(env=env).begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_models(env: str = 'postgres') -> None:
    async with get_engine(env=env).begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_session() -> AsyncSession:
    async with create_session() as session:
        yield session
