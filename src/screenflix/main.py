from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from screenflix.core.app.middlewares import RequestLogMiddleware
from screenflix.core.logging.config import setup_logging
from screenflix.core.settings import get_settings

from screenflix.modules.catalog.presentation.api.v1.router import router

settings = get_settings()

setup_logging(app_name=settings.app_name)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLogMiddleware)

app.include_router(router, prefix="/api/v1")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}