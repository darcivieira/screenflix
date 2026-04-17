from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

import screenflix.core.database as database


@pytest.mark.asyncio
async def test_get_engine_creates_and_caches(monkeypatch):
    fake_engine = object()

    monkeypatch.setattr(database, "_Engine", None)
    monkeypatch.setattr(database, "get_settings", lambda: SimpleNamespace(database_url="db://url", database_echo=True))

    create_engine_mock = Mock(return_value=fake_engine)
    monkeypatch.setattr(database, "create_async_engine", create_engine_mock)

    first = database.get_engine()
    second = database.get_engine()

    assert first is fake_engine
    assert second is fake_engine
    create_engine_mock.assert_called_once_with("db://url", echo=True, pool_size=20)


@pytest.mark.asyncio
async def test_get_session_maker_creates_and_caches(monkeypatch):
    fake_engine = object()
    fake_maker = object()

    monkeypatch.setattr(database, "_SessionMaker", None)
    monkeypatch.setattr(database, "get_engine", lambda: fake_engine)

    maker_factory = Mock(return_value=fake_maker)
    monkeypatch.setattr(database, "async_sessionmaker", maker_factory)

    first = database.get_session_maker()
    second = database.get_session_maker()

    assert first is fake_maker
    assert second is fake_maker
    maker_factory.assert_called_once_with(fake_engine, expire_on_commit=False, class_=database.AsyncSession)


@pytest.mark.asyncio
async def test_get_session_yields_session(monkeypatch):
    session = object()

    class FakeSessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    fake_maker = Mock(return_value=FakeSessionContext())
    monkeypatch.setattr(database, "get_session_maker", lambda: fake_maker)

    yielded = []
    async for current in database.get_session():
        yielded.append(current)

    assert yielded == [session]
