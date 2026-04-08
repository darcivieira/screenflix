from fastapi import APIRouter

from screenflix.modules.catalog.presentation.api.v1.enpoints import register_router, media_router


router = APIRouter()

router.include_router(register_router)
router.include_router(media_router)
