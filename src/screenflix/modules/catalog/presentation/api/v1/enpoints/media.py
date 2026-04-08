from fastapi import APIRouter

router = APIRouter(
    prefix="/media",
    tags=["Catalog"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
async def list_all_media():
    return []

@router.get("/{media_id}")
async def get_media(media_id: int):
    return {"id": media_id}

@router.get("/{media_id}/seasons")
async def list_seasons(media_id: int):
    return [{"id": media_id}]

@router.get("/{media_id}/seasons/{season_id}")
async def get_season(media_id: int, season_id: int):
    return {"id": season_id}

@router.get("/movies")
async def list_movies():
    return []

@router.get("/series")
async def list_series():
    return []

@router.get("/movies/top5")
async def list_top_five_movies():
    return []

@router.get("/series/top5")
async def list_top_five_series():
    return []