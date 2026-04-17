from datetime import date

import pytest
from pydantic import ValidationError

from screenflix.modules.catalog.presentation.api.v1.schemas.media import (
    EpisodeBaseSchema,
    EpisodeSchema,
    MediaBaseSchema,
    MediaSchema,
)
from screenflix.modules.catalog.presentation.api.v1.schemas.register import RegisterBody


def test_register_body_validation():
    assert RegisterBody(name="Dark").name == "Dark"

    with pytest.raises(ValidationError):
        RegisterBody(name="")


def test_media_and_episode_schema_models():
    media_base = MediaBaseSchema(
        id=1,
        title="Dark",
        original_title="Dark",
        poster_url="http://img",
        rating=8.8,
        plot="plot",
    )
    assert media_base.id == 1

    media = MediaSchema(
        id=1,
        title="Dark",
        original_title="Dark",
        poster_url="http://img",
        rating=8.8,
        year=2017,
        release_date=date(2017, 12, 1),
        genres="Drama",
        actors="Actor",
        writers="Writer",
        directors="Director",
        plot="plot",
    )
    assert media.year == 2017

    ep_base = EpisodeBaseSchema(id=1, original_title="EP", poster_url="http://img")
    assert ep_base.original_title == "EP"

    ep = EpisodeSchema(
        id=1,
        original_title="EP",
        title="EP",
        released=date(2020, 1, 1),
        poster_url="http://img",
        rating=7.5,
        plot="plot",
    )
    assert ep.rating == 7.5
