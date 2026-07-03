from pydantic import Field, BaseModel


class RegisterBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the movie or series")
