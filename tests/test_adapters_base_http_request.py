from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from httpx import HTTPStatusError, Request, Response

from screenflix.modules.catalog.adapters.base_http_request import BaseHttpRequest


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_perform_request_success(monkeypatch):
    captured = {}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, json=None, params=None):
            captured.update({"method": method, "url": url, "json": json, "params": params})
            return FakeResponse({"ok": True})

    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.base_http_request.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    request = BaseHttpRequest("http://example.com", headers={"Authorization": "Bearer x"}, timeout=12)
    result = await request._perform_request("POST", "/x", json={"a": 1}, params={"q": "1"})

    assert request.base_url == "http://example.com"
    assert request.timeout == 12
    assert request.headers["Authorization"] == "Bearer x"
    assert result == {"ok": True}
    assert captured == {"method": "POST", "url": "/x", "json": {"a": 1}, "params": {"q": "1"}}


@pytest.mark.asyncio
async def test_perform_request_raises_http_exception_on_http_status_error(monkeypatch):
    logger = Mock()
    monkeypatch.setattr("screenflix.modules.catalog.adapters.base_http_request.logger", logger)

    failing_response = Response(status_code=401, request=Request("GET", "http://example.com"), text="unauthorized")

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, *args, **kwargs):
            raise HTTPStatusError("unauthorized", request=failing_response.request, response=failing_response)

    monkeypatch.setattr(
        "screenflix.modules.catalog.adapters.base_http_request.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    request = BaseHttpRequest("http://example.com")
    with pytest.raises(HTTPException) as exc:
        await request._perform_request("GET", "/x")

    assert exc.value.status_code == 401
    assert exc.value.detail == "unauthorized"
    logger.error.assert_called_once()
