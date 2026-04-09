from sqlalchemy.ext.asyncio import AsyncSession

from screenflix.modules.catalog.domain.entities import Media, Episode
from screenflix.modules.catalog.infrastructure.repositories.media_repository import MediaRepository
from screenflix.modules.catalog.infrastructure.repositories.episode_repository import EpisodeRepository


class RepositoryFactor:
    def __init__(self, session: AsyncSession):
        self.media: MediaRepository = MediaRepository(session, Media)
        self.episode: EpisodeRepository = EpisodeRepository(session, Episode)