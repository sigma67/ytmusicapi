from pydantic import BaseModel


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int
