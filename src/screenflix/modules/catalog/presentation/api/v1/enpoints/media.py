from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from screenflix.core.app.dependencies import get_db_session
from screenflix.modules.catalog.domain.entities import episode
from screenflix.modules.catalog.infrastructure.repositories import RepositoryFactor
from screenflix.modules.catalog.presentation.api.v1.schemas.media import MediaListAll

router = APIRouter(
    prefix="/media",
    tags=["Catalog"],
    responses={404: {"description": "Not found"}},
)


async def get_media_service(session: AsyncSession = Depends(get_db_session)):
    return RepositoryFactor(session)


@router.get("", response_model=list[MediaListAll])
async def list_all_media(repository: RepositoryFactor = Depends(get_media_service)):
    data = await repository.media.list_all()
    return data

@router.get("/{media_id}")
async def get_media(media_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.get_by_id(media_id)
    return media

@router.get("/{media_id}/seasons")
async def list_seasons(media_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    return [{"id": media_id}]

@router.get("/{media_id}/seasons/{season_id}")
async def get_season(media_id: int, season_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    episodes = await repository.episode.list_all(media_id=media_id, season=season_id)
    return episodes

@router.get("/movies")
async def list_movies(repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.list_all(media_type="movie")
    return media

@router.get("/series")
async def list_series(repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.list_all(media_type="series")
    return media

@router.get("/movies/top5")
async def list_top_five_movies():
    return []

@router.get("/series/top5")
async def list_top_five_series():
    return []