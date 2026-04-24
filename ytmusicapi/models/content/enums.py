from enum import Enum
from typing import Any


class PrivacyStatus(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    UNLISTED = "UNLISTED"


class LikeStatus(str, Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    INDIFFERENT = "INDIFFERENT"

    @classmethod
    def _missing_(cls, value: Any) -> "LikeStatus":
        return cls.INDIFFERENT


class VideoType(str, Enum):
    OMV = "MUSIC_VIDEO_TYPE_OMV"
    UGC = "MUSIC_VIDEO_TYPE_UGC"
    ATV = "MUSIC_VIDEO_TYPE_ATV"
    OFFICIAL_SOURCE_MUSIC = "MUSIC_VIDEO_TYPE_OFFICIAL_SOURCE_MUSIC"


class PlaylistSortOrder(Enum):
    MANUAL = 0
    NEWEST_FIRST = 1
    NEWEST_LAST = 2
    TOP_VOTED = 6


class VoteStatus(str, Enum):
    UPVOTED = "VOTE_STATUS_UPVOTED"
    DOWNVOTED = "VOTE_STATUS_DOWNVOTED"
    UNSPECIFIED = "VOTE_STATUS_UNSPECIFIED"
