from datetime import date
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional, List

from sqlalchemy import String, Integer, Date, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from screenflix.core.database import Base, IDMixin, TimestampMixin


class MediaType(StrEnum):
    MOVIE = "movie"
    SERIES = "series"


@dataclass
class Media(Base, IDMixin, TimestampMixin):
    __tablename__ = "media"

    title: Mapped[str] = mapped_column(String(255), index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    media_type: Mapped[MediaType] = mapped_column(String(10), default=MediaType.MOVIE, index=True)
    year: Mapped[int] = mapped_column(Integer, default=None)
    release_date: Mapped[Optional[date]] = mapped_column(Date, default=None)
    plot: Mapped[str] = mapped_column(Text)
    genres: Mapped[Optional[str]] = mapped_column(Text, default=None)
    tags: Mapped[Optional[str]] = mapped_column(Text, default=None)
    actors: Mapped[Optional[str]] = mapped_column(Text, default=None)
    writers: Mapped[Optional[str]] = mapped_column(Text, default=None)
    directors: Mapped[Optional[str]] = mapped_column(Text, default=None)
    poster_url: Mapped[Optional[str]] = mapped_column(String)
    awards: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    rating: Mapped[Optional[float]] = mapped_column(Float, default=None)
    runtime: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    total_seasons: Mapped[Optional[int]] = mapped_column(Integer, default=None)

    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="series",
        cascade="all, delete-orphan",
        lazy="selectin",  # evita N+1 por padrão
    )

    def __repr__(self) -> str:
        return f"<Media {self.media_type}: {self.title} ({self.year})>"
