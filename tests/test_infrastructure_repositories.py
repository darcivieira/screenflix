import pytest

from screenflix.modules.catalog.domain.entities import Episode, Media
from screenflix.modules.catalog.infrastructure.repositories import EpisodeRepository, MediaRepository, RepositoryFactor


class FakeScalarOneOrNoneResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, result=None):
        self.result = result
        self.query = None

    async def execute(self, query):
        self.query = query
        return self.result


def test_repository_factor_initializes_sub_repositories():
    session = object()

    factor = RepositoryFactor(session)

    assert isinstance(factor.media, MediaRepository)
    assert isinstance(factor.episode, EpisodeRepository)
    assert factor.media.session is session
    assert factor.episode.session is session
    assert factor.media.model is Media
    assert factor.episode.model is Episode


@pytest.mark.asyncio
async def test_episode_repository_get_by_media_and_season_and_episode():
    expected = {"id": 77}
    session = FakeSession(FakeScalarOneOrNoneResult(expected))
    repo = EpisodeRepository(session, Episode)

    result = await repo.get_by_media_and_season_and_episode(media_id=10, season=2, episode=3)

    assert result == expected
    query_text = str(session.query)
    assert "episode.media_id" in query_text
    assert "episode.season" in query_text
    assert "episode.episode" in query_text
