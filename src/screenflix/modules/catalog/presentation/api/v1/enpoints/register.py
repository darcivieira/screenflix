import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from screenflix.core.app.dependencies import get_db_session
from screenflix.core.logging.logger import get_logger
from screenflix.modules.catalog.application.use_cases.register_data_workflow import RegisterDataWorkflow
from screenflix.modules.catalog.application.schemas.register import RegisterBody


logger = get_logger(__name__)

router = APIRouter(
    prefix="/register",
    tags=["Catalog"],
)


def _handle_background_task_result(task: asyncio.Task[None]) -> None:
    try:
        task.result()
    except Exception:
        logger.exception("Background register workflow failed", task_name=task.get_name())


async def _register_media(name: str):
    await asyncio.sleep(30)
    logger.info(f"Registered media: {name}")


@router.post("")
async def register(body: RegisterBody, session: AsyncSession = Depends(get_db_session)):
    try:
        workflow = RegisterDataWorkflow(session)
        task = asyncio.create_task(workflow.execute(body.name), name=f"register:{body.name}")
        task.add_done_callback(_handle_background_task_result)
        return {"message": "Media registration initiated"}
    except Exception as err:
        logger.error(err)
        raise HTTPException(status_code=500, detail="Internal Server Error")
