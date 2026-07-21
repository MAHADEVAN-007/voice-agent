import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv(override=True)

DATABASE_URL = os.environ.get("DATABASE_URL")

_engines: dict[int, object] = {}


def _get_engine():
    loop_id = id(asyncio.get_running_loop())
    if loop_id not in _engines:
        _engines[loop_id] = create_async_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engines[loop_id]


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def session_scope():
    maker = async_sessionmaker(
        _get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with maker() as db:
        yield db


async def get_db():
    async with session_scope() as db:
        yield db


async def init_db():
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
