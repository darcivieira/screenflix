from sqlalchemy.ext.asyncio import AsyncSession

from screenflix.modules.catalog.domain.entities import Episode
from screenflix.modules.catalog.infrastructure.repositories import RepositoryFactor


class EpisodeService:
    def __init__(self, session: AsyncSession):
        self.repository = RepositoryFactor(session)

    async def list_by_season(self, media_id: int, season: int) -> list[Episode]:
        return await self.repository.episode.list_all(media_id=media_id, season=season)

    async def get(self, media_id: int, season: int, episode: int) -> Episode | None:
        return await self.repository.episode.get_by_media_and_season_and_episode(
            media_id=media_id, season=season, episode=episode
        )
