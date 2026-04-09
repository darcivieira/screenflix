from pydantic import BaseModel


class MediaListAll(BaseModel):
    id: int
    title: str
    original_title: str
    plot: str
    poster_url: str