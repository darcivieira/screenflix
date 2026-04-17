from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from screenflix.modules.catalog.adapters.omdb_request import OmdbRequest


def test_omdb_request_init_uses_settings(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )

    omdb = OmdbRequest()

    assert omdb.base_url == "http://omdb.local"
    assert omdb._base_params["apikey"] == "abc"


def test_get_params_merges_base_and_input(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )
    omdb = OmdbRequest()

    result = omdb._get_params({"t": "Matrix"})

    assert result["apikey"] == "abc"
    assert result["t"] == "Matrix"


@pytest.mark.asyncio
async def test_get_episode_by_id_calls_perform_request(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )
    omdb = OmdbRequest()
    perform = AsyncMock(return_value={"imdbID": "tt1"})
    monkeypatch.setattr(omdb, "_perform_request", perform)

    result = await omdb.get_episode_by_id("tt1")

    assert result == {"imdbID": "tt1"}
    perform.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_series_episodes_by_season(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )
    omdb = OmdbRequest()

    season_payloads = {
        1: {"Response": "True", "Episodes": [{"imdbID": "tt-a"}, {"imdbID": "tt-b"}]},
        2: {"Response": "False"},
    }

    async def fake_perform_request(method, url=None, json=None, params=None):
        if "Season" in params:
            return season_payloads[params["Season"]]
        return {"imdbID": params["i"], "title": "Episode"}

    monkeypatch.setattr(omdb, "_perform_request", fake_perform_request)

    result = await omdb.get_series_episodes_by_season({"totalSeasons": "2", "imdbID": "tt-series"})

    assert len(result) == 2
    assert {item["imdbID"] for item in result} == {"tt-a", "tt-b"}


@pytest.mark.asyncio
async def test_get_media_by_title_for_series_fetches_episodes(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )
    omdb = OmdbRequest()

    perform = AsyncMock(return_value={"Type": "series", "imdbID": "tt-series", "totalSeasons": "1"})
    series_episodes = AsyncMock(return_value=[{"imdbID": "tt-ep"}])

    monkeypatch.setattr(omdb, "_perform_request", perform)
    monkeypatch.setattr(omdb, "get_series_episodes_by_season", series_episodes)

    result = await omdb.get_media_by_title("Dark")

    assert result["episodes"] == [{"imdbID": "tt-ep"}]


@pytest.mark.asyncio
async def test_get_media_by_title_for_movie_does_not_fetch_episodes(monkeypatch):
    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.omdb_request.get_settings",
        lambda: SimpleNamespace(omdb_api_key="abc", omdb_api_url="http://omdb.local"),
    )
    omdb = OmdbRequest()

    perform = AsyncMock(return_value={"Type": "movie", "imdbID": "tt-movie"})
    monkeypatch.setattr(omdb, "_perform_request", perform)
    series_episodes = AsyncMock()
    monkeypatch.setattr(omdb, "get_series_episodes_by_season", series_episodes)

    result = await omdb.get_media_by_title("Matrix")

    assert result == {"Type": "movie", "imdbID": "tt-movie"}
    series_episodes.assert_not_awaited()
