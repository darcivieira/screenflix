from screenflix.modules.catalog.domain.entities.episode import Episode
from screenflix.modules.catalog.domain.entities.media import Media, MediaType


def test_media_type_values():
    assert MediaType.MOVIE.value == "movie"
    assert MediaType.SERIES.value == "series"


def test_media_repr_uses_core_fields():
    media = Media(
        title="The Matrix",
        original_title="The Matrix",
        media_type=MediaType.MOVIE,
        year=1999,
        release_date=None,
        plot="plot",
        genres=None,
        tags=None,
        actors=None,
        writers=None,
        directors=None,
        poster_url="url",
        awards=None,
        rating=None,
        runtime=None,
        total_seasons=None,
    )

    assert repr(media) == "<Media movie: The Matrix (1999)>"


def test_episode_repr_uses_season_episode_and_title():
    episode = Episode(
        media_id=1,
        title="The Test Episode",
        original_title="The Test Episode",
        plot="plot",
        released=None,
        poster_url="url",
        season=2,
        episode=7,
        rating=None,
    )

    assert repr(episode) == "<Episode S02E07: The Test Episode>"
