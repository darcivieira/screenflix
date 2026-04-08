import asyncio

from fastapi import APIRouter

from screenflix.core.logging.logger import get_logger
from screenflix.modules.catalog.adapters.omdb_request import OmdbRequest
from screenflix.modules.catalog.adapters.openai_analyzer import OpenAIAnalyzer
from screenflix.modules.catalog.presentation.api.v1.schemas.register import RegisterBody


logger = get_logger(__name__)

router = APIRouter(
    prefix="/register",
    tags=["Catalog"],
)

async def _register_media(name: str):
    await asyncio.sleep(30)
    logger.info(f"Registered media: {name}")


@router.post("")
async def register(body: RegisterBody):
    asyncio.create_task(_register_media(body.name))
    service = OmdbRequest()
    data = await service.get_media_by_title(body.name)
    svc = OpenAIAnalyzer()
    data = await svc.analyze_data(data)
    return data