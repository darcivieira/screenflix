from __future__ import annotations

import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

from screenflix.core.settings import get_settings


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class IDMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


_Engine: Optional[AsyncEngine] = None
_SessionMaker: Optional[AsyncSession] = None

def get_engine() -> AsyncEngine:
    global _Engine
    if _Engine is None:
        sts = get_settings()
        _Engine = create_async_engine(sts.database_url, echo=sts.database_echo, pool_size=20)
    return _Engine

def get_session_maker() -> async_sessionmaker[AsyncSession]:
    global _SessionMaker
    if _SessionMaker is None:
        engine = get_engine()
        _SessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return _SessionMaker

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
