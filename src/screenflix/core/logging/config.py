import logging
import sys
from typing import List

import structlog
from structlog.contextvars import bind_contextvars

from screenflix.core.settings import get_settings

_LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def _resolve_log_level(log_level: str) -> int:
    return _LOG_LEVEL_MAP.get(log_level, logging.INFO)


def setup_logging(*, app_name: str):
    settings = get_settings()
    level_name = settings.log_level.upper()
    level = _resolve_log_level(level_name)

    renderer = structlog.processors.JSONRenderer()
    if level_name in ("DEBUG", "INFO"):
        renderer = structlog.dev.ConsoleRenderer()

    common_processors: List[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                renderer,
            ],
            foreign_pre_chain=common_processors,
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    structlog.configure(
        processors=[
            *common_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    bind_contextvars(app_name=app_name)
