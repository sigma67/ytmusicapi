from enum import Enum


class ResponseStatus(str, Enum):
    SUCCEEDED = "STATUS_SUCCEEDED"


class ProfileTypes(str, Enum):
    ARTIST = "ARTIST"
    USER = "USER"
    CHANNEL = "CHANNEL"  # Podcasts channel
