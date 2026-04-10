from sqlalchemy import select

from screenflix.core.repository import BaseRepository
from screenflix.modules.catalog.domain.entities import Episode


class EpisodeRepository(BaseRepository[Episode]):

    async def get_by_media_and_season_and_episode(self, media_id: int, season: int, episode: int):
        query = select(self.model).where(
            Episode.media_id == media_id,
            Episode.season == season,
            Episode.episode == episode
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()