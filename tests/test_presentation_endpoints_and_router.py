import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from screenflix.modules.catalog.presentation.api.v1 import router as v1_router_module
from screenflix.modules.catalog.presentation.api.v1.enpoints import media as media_endpoints
from screenflix.modules.catalog.presentation.api.v1.enpoints import register as register_endpoints
from screenflix.modules.catalog.application.schemas.register import RegisterBody


class FakeMediaService:
    def __init__(self):
        self.list_all = AsyncMock(return_value=[{"id": 1}])
        self.list_by_type = AsyncMock(return_value=[{"id": 1}])
        self.top_five = AsyncMock(return_value=[{"id": 1}])
        self.get = AsyncMock(return_value={"id": 1})


class FakeEpisodeService:
    def __init__(self):
        self.list_by_season = AsyncMock(return_value=[{"id": 2}])
        self.get = AsyncMock(return_value={"id": 3})


@pytest.mark.asyncio
async def test_router_includes_register_and_media_routes():
    paths = {route.path for route in v1_router_module.router.routes}
    assert "/register" in paths
    assert "/media" in paths


@pytest.mark.asyncio
async def test_get_media_service_builds_media_service(monkeypatch):
    fake = object()
    monkeypatch.setattr("screenflix.modules.catalog.presentation.api.v1.enpoints.media.MediaService", lambda session: fake)

    result = await media_endpoints.get_media_service(session=object())

    assert result is fake


@pytest.mark.asyncio
async def test_get_episode_service_builds_episode_service(monkeypatch):
    fake = object()
    monkeypatch.setattr("screenflix.modules.catalog.presentation.api.v1.enpoints.media.EpisodeService", lambda session: fake)

    result = await media_endpoints.get_episode_service(session=object())

    assert result is fake


@pytest.mark.asyncio
async def test_media_endpoints_happy_paths():
    media_service = FakeMediaService()
    episode_service = FakeEpisodeService()

    assert await media_endpoints.list_all_media(media_service) == [{"id": 1}]
    assert await media_endpoints.list_movies(media_service) == [{"id": 1}]
    assert await media_endpoints.list_series(media_service) == [{"id": 1}]
    assert await media_endpoints.list_top_five_movies(media_service) == [{"id": 1}]
    assert await media_endpoints.list_top_five_series(media_service) == [{"id": 1}]
    assert await media_endpoints.get_media(1, media_service) == {"id": 1}
    assert await media_endpoints.list_episodes_by_season(1, 1, episode_service) == [{"id": 2}]
    assert await media_endpoints.get_episode_by_season(1, 1, 1, episode_service) == {"id": 3}


@pytest.mark.asyncio
async def test_media_endpoint_media_not_found():
    media_service = FakeMediaService()
    media_service.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await media_endpoints.get_media(1, media_service)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Media not found"


@pytest.mark.asyncio
async def test_media_endpoint_episode_not_found():
    episode_service = FakeEpisodeService()
    episode_service.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await media_endpoints.get_episode_by_season(1, 1, 1, episode_service)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Episode not found"


@pytest.mark.asyncio
async def test_register_endpoint_success(monkeypatch):
    created_tasks = []

    class FakeTask:
        def __init__(self):
            self.callbacks = []

        def add_done_callback(self, callback):
            self.callbacks.append(callback)

        def get_name(self):
            return "register:Matrix"

        def result(self):
            return None

    fake_task = FakeTask()

    class FakeWorkflow:
        def __init__(self, session):
            self.session = session
            self.execute = AsyncMock(return_value=None)

    monkeypatch.setattr(register_endpoints, "RegisterDataWorkflow", FakeWorkflow)

    def fake_create_task(coro, name=None):
        assert name == "register:Matrix"
        created_tasks.append((coro, name))
        coro.close()
        return fake_task

    monkeypatch.setattr(register_endpoints.asyncio, "create_task", fake_create_task)

    response = await register_endpoints.register(RegisterBody(name="Matrix"), session=object())

    assert response == {"message": "Media registration initiated"}
    assert len(created_tasks) == 1
    assert len(fake_task.callbacks) == 1


@pytest.mark.asyncio
async def test_register_endpoint_returns_500_on_failure(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(register_endpoints, "logger", logger)

    class BrokenWorkflow:
        def __init__(self, session):
            raise RuntimeError("boom")

    monkeypatch.setattr(register_endpoints, "RegisterDataWorkflow", BrokenWorkflow)

    with pytest.raises(HTTPException) as exc:
        await register_endpoints.register(RegisterBody(name="Matrix"), session=object())

    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal Server Error"
    logger.error.assert_called_once()


def test_handle_background_task_result_logs_exceptions(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(register_endpoints, "logger", logger)

    class FailingTask:
        def result(self):
            raise RuntimeError("task failed")

        def get_name(self):
            return "register:Broken"

    task = FailingTask()

    register_endpoints._handle_background_task_result(task)

    logger.exception.assert_called_once()
