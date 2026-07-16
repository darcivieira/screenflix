from unittest.mock import AsyncMock, MagicMock

import pytest

from screenflix.modules.catalog.application.schemas.media import MediaCountSchema
from screenflix.modules.catalog.application.services.media_service import MediaService
from screenflix.modules.catalog.presentation.api.v1.enpoints import media as media_endpoints


class FakeMediaService:
    def __init__(self, total: int = 3):
        self.count = AsyncMock(return_value=total)


# ── Presentation: o endpoint /media/count ───────────────────────────
@pytest.mark.asyncio
async def test_count_media_happy_path():
    service = FakeMediaService(total=7)

    result = await media_endpoints.count_media(media_type=None, service=service)

    assert isinstance(result, MediaCountSchema)
    assert result.total == 7
    service.count.assert_awaited_once_with(media_type=None)


@pytest.mark.asyncio
async def test_count_media_filters_by_type():
    service = FakeMediaService(total=2)

    result = await media_endpoints.count_media(media_type="movie", service=service)

    assert result.total == 2
    service.count.assert_awaited_once_with(media_type="movie")


@pytest.mark.asyncio
async def test_count_route_is_registered_before_media_id():
    # /media/count precisa ser resolvida antes de /media/{media_id}
    paths = [route.path for route in media_endpoints.router.routes]
    assert "/media/count" in paths
    assert paths.index("/media/count") < paths.index("/media/{media_id}")


# ── Application: MediaService.count delega ao repositório ────────────
@pytest.mark.asyncio
async def test_media_service_count_delegates_to_repository():
    service = MediaService(session=MagicMock())
    service.repository.media.count = AsyncMock(return_value=5)

    total = await service.count(media_type="series")

    assert total == 5
    service.repository.media.count.assert_awaited_once_with(media_type="series")
