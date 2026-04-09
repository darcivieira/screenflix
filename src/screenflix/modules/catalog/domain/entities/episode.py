from datetime import date
from typing import Optional

from sqlalchemy import String, Text, Date, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from screenflix.core.database import Base, IDMixin, TimestampMixin


class Episode(Base, IDMixin, TimestampMixin):
    __tablename__ = "episode"

    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"), nullable=False)
    title: Mapped[str] = mapped_column(String)
    original_title: Mapped[str] = mapped_column(String)
    plot: Mapped[str] = mapped_column(Text)
    released: Mapped[Optional[date]] = mapped_column(Date, default=None)
    poster_url: Mapped[Optional[str]] = mapped_column(String)
    season: Mapped[int] = mapped_column(Integer)
    episode: Mapped[int] = mapped_column(Integer)
    rating: Mapped[Optional[float]] = mapped_column(Float, default=None)

    series: Mapped["Media"] = relationship(back_populates="episodes")

    def __repr__(self) -> str:
        return f"<Episode S{self.season:02d}E{self.episode:02d}: {self.title}>"
