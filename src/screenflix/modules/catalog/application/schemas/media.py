from datetime import date
from typing import Optional

from pydantic import BaseModel


class MediaBaseSchema(BaseModel):
    id: int
    title: str
    original_title: str
    poster_url: str
    rating: float
    plot: str

class EpisodeBaseSchema(BaseModel):
    id: int
    original_title: str
    poster_url: str


class MediaSchema(BaseModel):
    id: int
    title: str
    original_title: str
    poster_url: str
    rating: float
    year: int
    release_date: Optional[date]
    genres: str
    actors: str
    writers: str
    directors: str
    plot: str


class EpisodeSchema(BaseModel):
    id: int
    original_title: str
    title: str
    released: Optional[date]
    poster_url: str
    rating: float
    plot: str
