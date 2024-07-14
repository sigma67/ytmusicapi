from pydantic import BaseModel, Field

from ytmusicapi.models.content.generic import User


class SearchResult(BaseModel):
    category: str
    result_type: str = Field(..., alias="resultType")


class VideoSearchResult(SearchResult):
    result_type = "video"
    video_id: str = Field(..., alias="videoId")
    title: str = Field(..., alias="title")
    artists: list[User]
    views: str
    video_type: str = Field(..., alias="videoType")
    duration: str
    duration_seconds: int
