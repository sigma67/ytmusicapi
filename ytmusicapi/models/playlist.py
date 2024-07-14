from typing import Optional

from pydantic import BaseModel, Field

from ytmusicapi.models.content.enums import LikeStatus, PrivacyStatus, VideoType
from ytmusicapi.models.content.generic import Album, User
from ytmusicapi.models.thumbnail import Thumbnail


class FeedbackTokens(BaseModel):
    add: str
    remove: str


class PlaylistItem(BaseModel):
    video_id: Optional[str] = Field(alias="videoId")
    title: str
    artists: list[User]
    album: Optional[Album]
    duration: str
    like_status: LikeStatus = Field(alias="likeStatus")
    thumbnails: list[Thumbnail]

    is_available: bool = Field(alias="isAvailable")
    is_explicit: bool = Field(alias="isExplicit")

    video_type: Optional[VideoType] = Field(alias="videoType")
    feedback_tokens: Optional[FeedbackTokens] = Field(default=None, alias="feedbackTokens")
    set_video_id: Optional[str] = Field(default=None, alias="setVideoId")


class PlaylistResult(BaseModel):
    id: str
    privacy: PrivacyStatus
    title: str
    thumbnails: list[Thumbnail]
    description: Optional[str]
    author: str
    year: str
    duration: str
    duration_seconds: int
    track_count: Optional[str] = None

    suggestions: list[PlaylistItem] = []
    tracks: list[PlaylistItem] = []

    related: list[dict] = []
