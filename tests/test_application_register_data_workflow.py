from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from screenflix.modules.catalog.application.use_cases.register_data_workflow import RegisterDataWorkflow


class FakeSession:
    def __init__(self):
        self.added = []
        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0

    def add(self, entity):
        self.added.append(entity)

    async def flush(self):
        self.flush_calls += 1
        if self.added:
            media = self.added[0]
            setattr(media, "id", 123)

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1


@pytest.fixture
def workflow(monkeypatch):
    omdb = Mock()
    analyzer = Mock()
    logger = Mock()

    monkeypatch.setattr(
        "screenflix.modules.catalog.application.use_cases.register_data_workflow.OmdbRequest",
        lambda: omdb,
    )
    monkeypatch.setattr(
        "screenflix.modules.catalog.application.use_cases.register_data_workflow.OpenAIAnalyzer",
        lambda: analyzer,
    )
    monkeypatch.setattr(
        "screenflix.modules.catalog.application.use_cases.register_data_workflow.get_logger",
        lambda name: logger,
    )

    current = RegisterDataWorkflow(FakeSession())
    current.omdb_request = omdb
    current.openai_analyzer = analyzer
    current.logger = logger
    return current


def test_parse_date_extract_year_and_to_int():
    assert RegisterDataWorkflow._parse_date("2024-01-10") == date(2024, 1, 10)
    assert RegisterDataWorkflow._parse_date("invalid") is None
    assert RegisterDataWorkflow._extract_year("1999-2001") == 1999
    assert RegisterDataWorkflow._extract_year("N/A") is None
    assert RegisterDataWorkflow._to_int("42") == 42
    assert RegisterDataWorkflow._to_int("4x") is None


def test_normalize_media_payload_joins_lists_and_infers_year_from_release_date():
    media_dict = {
        "release_date": "2020-02-03",
        "genres": ["Drama", "Sci-Fi"],
        "tags": ["future"],
        "actors": ["A", "B"],
        "writers": ["W"],
        "directors": ["D"],
        "year": None,
    }

    result = RegisterDataWorkflow._normalize_media_payload(media_dict, source_media_dict={})

    assert result["release_date"] == date(2020, 2, 3)
    assert result["year"] == 2020
    assert result["genres"] == "Drama, Sci-Fi"


def test_normalize_media_payload_raises_when_year_is_missing():
    with pytest.raises(ValueError, match="infer media year"):
        RegisterDataWorkflow._normalize_media_payload({"release_date": None, "year": None}, {})


def test_normalize_episode_payload_filters_and_coerces():
    payload = {
        "title": "Episode",
        "released": "2021-01-02",
        "season": "3",
        "episode": 7.0,
        "rating": 8.9,
        "unknown": "ignored",
    }

    result = RegisterDataWorkflow._normalize_episode_payload(payload)

    assert "unknown" not in result
    assert result["released"] == date(2021, 1, 2)
    assert result["season"] == 3
    assert result["episode"] == 7


@pytest.mark.asyncio
async def test_get_media_and_episodes_for_series(workflow):
    workflow.omdb_request.get_media_by_title = AsyncMock(
        return_value={"Type": "series", "episodes": [{"id": 1}], "Title": "Dark"}
    )

    media, episodes = await workflow._get_media_and_episodes("Dark")

    assert media == {"Type": "series", "Title": "Dark"}
    assert episodes == [{"id": 1}]


@pytest.mark.asyncio
async def test_get_media_and_episodes_for_movie(workflow):
    workflow.omdb_request.get_media_by_title = AsyncMock(return_value={"Type": "movie", "Title": "Matrix"})

    media, episodes = await workflow._get_media_and_episodes("Matrix")

    assert media == {"Type": "movie", "Title": "Matrix"}
    assert episodes == []


@pytest.mark.asyncio
async def test_analyze_episode_adds_media_id(workflow):
    workflow.openai_analyzer.analyze_data = AsyncMock(
        return_value={
            "title": "Ep1",
            "original_title": "Ep1",
            "plot": "plot",
            "released": "2020-01-01",
            "poster_url": "url",
            "season": "1",
            "episode": "2",
            "rating": 8.1,
        }
    )

    result = await workflow._analyze_episode({"Episode": 2}, media_id=999)

    assert result["media_id"] == 999
    assert result["season"] == 1
    assert result["episode"] == 2


@pytest.mark.asyncio
async def test_execute_commits_movie_without_episodes(workflow):
    session = FakeSession()
    workflow.session = session
    workflow._get_media_and_episodes = AsyncMock(return_value=({"Year": "1999"}, []))
    workflow.openai_analyzer.analyze_data = AsyncMock(
        return_value={
            "title": "Matrix",
            "original_title": "The Matrix",
            "media_type": "movie",
            "year": 1999,
            "release_date": "1999-03-31",
            "plot": "plot",
            "genres": ["Sci-Fi"],
            "tags": ["cyberpunk"],
            "actors": ["Keanu"],
            "writers": ["Wachowski"],
            "directors": ["Wachowski"],
            "poster_url": "url",
            "awards": "award",
            "rating": 9.0,
            "runtime": 136,
            "total_seasons": None,
        }
    )

    await workflow.execute("Matrix")

    assert session.flush_calls == 1
    assert session.commit_calls == 1
    assert session.rollback_calls == 0
    assert len(session.added) == 1


@pytest.mark.asyncio
async def test_execute_commits_series_with_episodes(workflow):
    session = FakeSession()
    workflow.session = session
    workflow._get_media_and_episodes = AsyncMock(return_value=({"Year": "2019"}, [{"Episode": 1}]))
    workflow.openai_analyzer.analyze_data = AsyncMock(
        side_effect=[
            {
                "title": "Dark",
                "original_title": "Dark",
                "media_type": "series",
                "year": 2019,
                "release_date": "2019-01-01",
                "plot": "plot",
                "genres": ["Drama"],
                "tags": ["mystery"],
                "actors": ["A"],
                "writers": ["W"],
                "directors": ["D"],
                "poster_url": "url",
                "awards": "award",
                "rating": 8.5,
                "runtime": 50,
                "total_seasons": 3,
            },
            {
                "title": "Ep1",
                "original_title": "Ep1",
                "plot": "plot",
                "released": "2019-01-02",
                "poster_url": "url",
                "season": "1",
                "episode": "1",
                "rating": 8.0,
            },
        ]
    )

    await workflow.execute("Dark")

    assert session.commit_calls == 1
    assert session.rollback_calls == 0
    # media + episode
    assert len(session.added) == 2


@pytest.mark.asyncio
async def test_execute_rolls_back_on_failure(workflow):
    session = FakeSession()
    workflow.session = session
    workflow._get_media_and_episodes = AsyncMock(side_effect=RuntimeError("upstream failed"))

    with pytest.raises(RuntimeError, match="upstream failed"):
        await workflow.execute("Broken")

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    workflow.logger.exception.assert_called_once()
