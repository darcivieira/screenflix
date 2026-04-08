from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from screenflix.core.logging.context import bind_request_context, clear_context, set_trace_id_context
from screenflix.core.logging.logger import get_logger

logger = get_logger(__name__)


class RequestLogMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started_at = perf_counter()
        clear_context()
        set_trace_id_context()
        bind_request_context(
            request.headers.get('user_id'),
            request.headers.get('site'),
            request.url.path,
            request.method,
        )
        try:
            response = await call_next(request)
            logger.info(
                "request.completed",
                status_code=response.status_code,
                duration_ms=round((perf_counter() - started_at) * 1000, 2),
            )
            return response
        except Exception:
            logger.exception("request.failed")
            raise
        finally:
            clear_context()
