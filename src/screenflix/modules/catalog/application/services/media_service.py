from sqlalchemy.ext.asyncio import AsyncSession

from screenflix.modules.catalog.domain.entities import Media
from screenflix.modules.catalog.infrastructure.repositories import RepositoryFactor


class MediaService:
    def __init__(self, session: AsyncSession):
        self.repository = RepositoryFactor(session)

    async def list_all(self) -> list[Media]:
        return await self.repository.media.list_all()

    async def list_by_type(self, media_type: str) -> list[Media]:
        return await self.repository.media.list_all(media_type=media_type)

    async def top_five(self, media_type: str) -> list[Media]:
        return await self.repository.media.list_all(
            limit=5, media_type=media_type, order_by="rating", desc=True
        )

    async def get(self, media_id: int) -> Media | None:
        return await self.repository.media.get_by_id(media_id)
