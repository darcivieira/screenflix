from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from screenflix.core.app.dependencies import get_db_session
from screenflix.core.logging.logger import get_logger
from screenflix.modules.catalog.infrastructure.repositories import RepositoryFactor
from screenflix.modules.catalog.presentation.api.v1.schemas.media import MediaBaseSchema, MediaSchema, \
    EpisodeBaseSchema, EpisodeSchema

logger = get_logger(__name__)

router = APIRouter(
    prefix="/media",
    tags=["Catalog"],
    responses={404: {"description": "Not found"}},
)


async def get_media_service(session: AsyncSession = Depends(get_db_session)):
    return RepositoryFactor(session)


@router.get("", response_model=list[MediaBaseSchema])
async def list_all_media(repository: RepositoryFactor = Depends(get_media_service)):
    data = await repository.media.list_all()
    return data

@router.get("/movies", response_model=list[MediaBaseSchema])
async def list_movies(repository: RepositoryFactor = Depends(get_media_service)):
    logger.info(f"Listing movies")
    media = await repository.media.list_all(media_type="movie")
    return media

@router.get("/series", response_model=list[MediaBaseSchema])
async def list_series(repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.list_all(media_type="series")
    return media

@router.get("/movies/top5", response_model=list[MediaBaseSchema])
async def list_top_five_movies(repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.list_all(limit=5, media_type="movie", order_by="rating", desc=True)
    return media

@router.get("/series/top5", response_model=list[MediaBaseSchema])
async def list_top_five_series(repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.list_all(limit=5, media_type="series", order_by="rating", desc=True)
    return media

@router.get("/{media_id}", response_model=MediaSchema)
async def get_media(media_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    media = await repository.media.get_by_id(media_id)
    return media

@router.get("/{media_id}/seasons/{season_id}", response_model=list[EpisodeBaseSchema])
async def list_episodes_by_season(media_id: int, season_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    episodes = await repository.episode.list_all(media_id=media_id, season=season_id)
    return episodes

@router.get("/{media_id}/seasons/{season_id}/episode/{episode_id}", response_model=EpisodeSchema)
async def list_episodes_by_season(media_id: int, season_id: int, episode_id: int, repository: RepositoryFactor = Depends(get_media_service)):
    episode = await repository.episode.get_by_media_and_season_and_episode(media_id=media_id, season=season_id, episode=episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

