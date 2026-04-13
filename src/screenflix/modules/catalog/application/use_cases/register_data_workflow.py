import asyncio
import re
from datetime import date, datetime
from typing import Any, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from screenflix.core.logging.logger import get_logger
from screenflix.modules.catalog.adapters.omdb_request import OmdbRequest
from screenflix.modules.catalog.adapters.openai_analyzer import OpenAIAnalyzer
from screenflix.modules.catalog.domain.entities import Media, Episode


class RegisterDataWorkflow:
    _EPISODE_ALLOWED_FIELDS = {
        "title",
        "original_title",
        "plot",
        "released",
        "poster_url",
        "season",
        "episode",
        "rating",
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.omdb_request = OmdbRequest()
        self.openai_analyzer = OpenAIAnalyzer()
        self.logger = get_logger(__name__)
        self.logger.info("RegisterDataWorkflow initialized")
        self.semaphore = asyncio.Semaphore(3)

    async def _get_media_and_episodes(self, media_name: str) -> Tuple[dict, List[dict]]:
        media = await self.omdb_request.get_media_by_title(media_name)
        if media.get("Type") == "series":
            episodes = media.pop("episodes")
            return media, episodes
        return media, []

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if isinstance(value, date):
            return value

        if isinstance(value, str) and value:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None

        return None

    @staticmethod
    def _extract_year(value: Any) -> int | None:
        if isinstance(value, int):
            return value

        if isinstance(value, float) and value.is_integer():
            return int(value)

        if isinstance(value, str):
            normalized = value.strip()
            if not normalized or normalized.upper() == "N/A":
                return None

            match = re.search(r"(19|20)\d{2}", normalized)
            if match:
                return int(match.group(0))

        return None

    @classmethod
    def _normalize_media_payload(cls, media_dict: dict, source_media_dict: dict) -> dict:
        release_date = cls._parse_date(media_dict.get("release_date"))
        media_dict["release_date"] = release_date

        for field in ("genres", "tags", "actors", "writers", "directors"):
            value = media_dict.get(field)
            if isinstance(value, list):
                media_dict[field] = ", ".join(value)

        year = cls._extract_year(media_dict.get("year"))
        if year is None and release_date is not None:
            year = release_date.year
        if year is None:
            year = cls._extract_year(source_media_dict.get("year"))
        if year is None:
            year = cls._extract_year(source_media_dict.get("Year"))
        if year is None:
            raise ValueError("Unable to infer media year from media payload")

        media_dict["year"] = year
        return media_dict

    @classmethod
    def _to_int(cls, value: Any) -> int | None:
        if isinstance(value, int):
            return value

        if isinstance(value, float) and value.is_integer():
            return int(value)

        if isinstance(value, str):
            normalized = value.strip()
            if normalized.isdigit():
                return int(normalized)

        return None

    @classmethod
    def _normalize_episode_payload(cls, episode_dict: dict) -> dict:
        normalized_episode = {
            key: value
            for key, value in episode_dict.items()
            if key in cls._EPISODE_ALLOWED_FIELDS
        }
        normalized_episode["released"] = cls._parse_date(normalized_episode.get("released"))
        normalized_episode["season"] = cls._to_int(normalized_episode.get("season"))
        normalized_episode["episode"] = cls._to_int(normalized_episode.get("episode"))
        return normalized_episode

    async def _analyze_episode(self, episode: dict, media_id: int) -> dict:
        async with self.semaphore:
            analyzed = await self.openai_analyzer.analyze_data(
                episode,
                payload_type="episode",
            )
            normalized = self._normalize_episode_payload(analyzed)
            normalized["media_id"] = media_id
            return normalized

    async def execute(self, media_name: str):
        try:
            source_media_dict, episodes = await self._get_media_and_episodes(media_name)
            analyzed_media_dict = await self.openai_analyzer.analyze_data(
                source_media_dict,
                payload_type="media",
            )
            media_dict = self._normalize_media_payload(analyzed_media_dict, source_media_dict)

            media = Media(**media_dict)
            self.session.add(media)
            await self.session.flush()
            media_id = media.id

            analyzed_episodes = await asyncio.gather(
                *(self._analyze_episode(episode, media_id) for episode in episodes)
            )

            for episode in analyzed_episodes:
                episode_obj = Episode(**episode)
                self.session.add(episode_obj)

            await self.session.commit()
        except Exception:
            await self.session.rollback()
            self.logger.exception("RegisterDataWorkflow execution failed", media_name=media_name)
            raise
