from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@db:5432/postgres'
SECRET_KEY: str = os.getenv('SECRET_KEY')

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
