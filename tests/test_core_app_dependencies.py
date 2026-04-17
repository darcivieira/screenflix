import pytest

from screenflix.core.app.dependencies import get_db_session


@pytest.mark.asyncio
async def test_get_db_session_yields_from_session_maker(monkeypatch):
    expected_session = object()

    class FakeContext:
        async def __aenter__(self):
            return expected_session

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def fake_get_session_maker():
        return lambda: FakeContext()

    monkeypatch.setattr("screenflix.core.app.dependencies.get_session_maker", fake_get_session_maker)

    yielded = []
    async for session in get_db_session():
        yielded.append(session)

    assert yielded == [expected_session]
