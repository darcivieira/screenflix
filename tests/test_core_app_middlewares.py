from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from screenflix.core.app.middlewares import RequestLogMiddleware


@pytest.mark.asyncio
async def test_request_log_middleware_success(monkeypatch):
    app = FastAPI()
    middleware = RequestLogMiddleware(app)

    clear_context = Mock()
    set_trace_id = Mock()
    bind_request_context = Mock()
    logger = Mock()

    monkeypatch.setattr("screenflix.core.app.middlewares.clear_context", clear_context)
    monkeypatch.setattr("screenflix.core.app.middlewares.set_trace_id_context", set_trace_id)
    monkeypatch.setattr("screenflix.core.app.middlewares.bind_request_context", bind_request_context)
    monkeypatch.setattr("screenflix.core.app.middlewares.logger", logger)
    monkeypatch.setattr("screenflix.core.app.middlewares.perf_counter", Mock(side_effect=[10.0, 10.5]))

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/healthz",
        "headers": [(b"user_id", b"42"), (b"site", b"BR")],
        "query_string": b"",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("127.0.0.1", 1234),
    }
    request = Request(scope)

    async def call_next(_request):
        return Response(status_code=204)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 204
    assert clear_context.call_count == 2
    set_trace_id.assert_called_once_with()
    bind_request_context.assert_called_once_with("42", "BR", "/healthz", "GET")
    logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_request_log_middleware_exception(monkeypatch):
    app = FastAPI()
    middleware = RequestLogMiddleware(app)

    clear_context = Mock()
    logger = Mock()

    monkeypatch.setattr("screenflix.core.app.middlewares.clear_context", clear_context)
    monkeypatch.setattr("screenflix.core.app.middlewares.set_trace_id_context", Mock())
    monkeypatch.setattr("screenflix.core.app.middlewares.bind_request_context", Mock())
    monkeypatch.setattr("screenflix.core.app.middlewares.logger", logger)
    monkeypatch.setattr("screenflix.core.app.middlewares.perf_counter", Mock(return_value=1.0))

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/register",
        "headers": [],
        "query_string": b"",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("127.0.0.1", 1234),
    }
    request = Request(scope)

    async def call_next(_request):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await middleware.dispatch(request, call_next)

    logger.exception.assert_called_once_with("request.failed")
    assert clear_context.call_count == 2
