import asyncio

from screenflix.core.logging.logger import get_logger
from screenflix.core.settings import get_settings
from screenflix.modules.catalog.adapters.base_http_request import BaseHttpRequest
from screenflix.modules.catalog.domain.entities.media import MediaType

logger = get_logger(__name__)


class OmdbRequest(BaseHttpRequest):

    _base_params: dict = {"apikey": "YOUR_API_KEY"}

    def __init__(self):
        settings = get_settings()
        self._base_params["apikey"] = settings.omdb_api_key
        super().__init__(base_url=settings.omdb_api_url)

    def _get_params(self, params: dict) -> dict:
        _params = self._base_params.copy()
        _params.update(params)
        return _params


    async def get_episode_by_id(self, imdb_id: str) -> dict:
        params = self._get_params({"i": imdb_id})
        resp = await self._perform_request("GET", params=params)
        return resp

    async def get_series_episodes_by_season(self, data: dict) -> list:
        result: list = []

        for season in range(1, int(data["totalSeasons"]) + 1):
            params = self._get_params({"i": data["imdbID"], "Season": season})
            resp = await self._perform_request("GET", params=params)

            if resp.get("Response") == "True":
                imdb_ids = [episode["imdbID"] for episode in resp["Episodes"]]
                r = await asyncio.gather(*[self.get_episode_by_id(imdb_id) for imdb_id in imdb_ids])
                result.extend(r)

        return result


    async def get_media_by_title(self, title: str) -> dict:
         data = await self._perform_request("GET", params=self._get_params({"t": title}))
         if data.get("Type") == MediaType.SERIES.value:
             data["episodes"] = await self.get_series_episodes_by_season(data)
         return data