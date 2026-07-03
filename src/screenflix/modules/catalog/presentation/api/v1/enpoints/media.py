from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from screenflix.core.app.dependencies import get_db_session
from screenflix.core.logging.logger import get_logger
from screenflix.modules.catalog.application.schemas.media import MediaBaseSchema, MediaSchema, \
    EpisodeBaseSchema, EpisodeSchema
from screenflix.modules.catalog.application.services import MediaService, EpisodeService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/media",
    tags=["Catalog"],
    responses={404: {"description": "Not found"}},
)


async def get_media_service(session: AsyncSession = Depends(get_db_session)) -> MediaService:
    return MediaService(session)


async def get_episode_service(session: AsyncSession = Depends(get_db_session)) -> EpisodeService:
    return EpisodeService(session)


@router.get("", response_model=list[MediaBaseSchema])
async def list_all_media(service: MediaService = Depends(get_media_service)):
    return await service.list_all()

@router.get("/movies", response_model=list[MediaBaseSchema])
async def list_movies(service: MediaService = Depends(get_media_service)):
    logger.info(f"Listing movies")
    return await service.list_by_type(media_type="movie")

@router.get("/series", response_model=list[MediaBaseSchema])
async def list_series(service: MediaService = Depends(get_media_service)):
    return await service.list_by_type(media_type="series")

@router.get("/movies/top5", response_model=list[MediaBaseSchema])
async def list_top_five_movies(service: MediaService = Depends(get_media_service)):
    return await service.top_five(media_type="movie")

@router.get("/series/top5", response_model=list[MediaBaseSchema])
async def list_top_five_series(service: MediaService = Depends(get_media_service)):
    return await service.top_five(media_type="series")

@router.get("/{media_id}", response_model=MediaSchema)
async def get_media(media_id: int, service: MediaService = Depends(get_media_service)):
    media = await service.get(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.get("/{media_id}/seasons/{season_id}", response_model=list[EpisodeBaseSchema])
async def list_episodes_by_season(media_id: int, season_id: int, service: EpisodeService = Depends(get_episode_service)):
    return await service.list_by_season(media_id=media_id, season=season_id)

@router.get("/{media_id}/seasons/{season_id}/episode/{episode_id}", response_model=EpisodeSchema)
async def get_episode_by_season(media_id: int, season_id: int, episode_id: int, service: EpisodeService = Depends(get_episode_service)):
    episode = await service.get(media_id=media_id, season=season_id, episode=episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode
