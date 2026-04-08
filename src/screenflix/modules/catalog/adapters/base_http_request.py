from typing import Optional

from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError

from screenflix.core.logging.logger import get_logger

logger = get_logger(__name__)

_HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}

class BaseHttpRequest:

    def __init__(self, base_url: str, *, headers: Optional[dict] = None, timeout: int = 30):
        self._base_url = base_url
        self._headers = _HEADERS
        if headers:
            self._headers.update(headers)
        self._timeout = timeout

    @property
    def base_url(self) -> str: return self._base_url

    @property
    def headers(self) -> dict: return self._headers

    @property
    def timeout(self) -> int: return self._timeout


    async def _perform_request(self, method: str, url: Optional[str] = None, *, json: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        async with AsyncClient(base_url=self.base_url, headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.request(method, url or self.base_url, json=json, params=params)
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as e:
                logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)