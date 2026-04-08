from typing import Optional

from httpx import AsyncClient

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
            response = await client.request(method, url or self.base_url, json=json, params=params)
            response.raise_for_status()
            return response.json()