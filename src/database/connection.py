from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY: str = os.getenv('SECRET_KEY')

Base = declarative_base()

class Settings:
    def __init__(self, env: str = 'postgres') -> None:
        self.env = env

    @staticmethod
    def get_engine(env: str):
        DATABASE_URL: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/{env}'
        engine = create_async_engine(DATABASE_URL, echo=True)
        return engine

    async def init_models(self) -> None:
        async with Settings.get_engine(self.env).begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_models(self) -> None:
        async with Settings.get_engine(self.env).begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        async_session = async_sessionmaker(Settings.get_engine(self.env), class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session
