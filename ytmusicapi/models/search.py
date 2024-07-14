from pydantic import BaseModel, Field


class Artist(BaseModel):
    name: str
    id: str | None


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int


class Album(BaseModel):
    name: str
    id: str


class FeedbackTokens(BaseModel):
    add: str
    remove: str


class SearchResult(BaseModel):
    category: str
    result_type: str = Field(..., alias="resultType")
    subscribers: str
    artists: list[Artist] = []
    thumbnails: list[Thumbnail]
    title: str
    album: Album
    in_library: bool = Field(..., alias="inLibrary")
    feedback_tokens: FeedbackTokens = Field(..., alias="feedbackTokens")
    video_id: str = Field(..., alias="videoId")
    video_type: str = Field(..., alias="videoType")
    duration: str
    year: str
    duration_seconds: int
    is_explicit: bool = Field(..., alias="isExplicit")
    type: str
    browse_id: str = Field(..., alias="browseId")
    views: str
    item_count: str = Field(..., alias="itemCount")
    author: str
    artist: str
    shuffle_id: str = Field(..., alias="shuffleId")
    radio_id: str = Field(..., alias="radioId")
    name: str


class Run(BaseModel):
    text: str
    bold: bool | None = None


class ModelItem(BaseModel):
    text: str
    runs: list[Run]
    from_history: bool = Field(..., alias="fromHistory")
