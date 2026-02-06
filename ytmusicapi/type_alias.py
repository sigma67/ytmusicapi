from collections.abc import Callable
from typing import Any, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

JsonDict = dict[str, Any]
JsonList = list[JsonDict]

RequestFuncType = Callable[[str], JsonDict]
RequestFuncBodyType = Callable[[JsonDict], JsonDict]
ParseFuncType = Callable[[JsonList], JsonList]
ParseFuncDictType = Callable[[JsonDict], JsonDict]


CATEGORY_T = TypeVar("CATEGORY_T")


class CategoryDict(Generic[CATEGORY_T], TypedDict):
    browseId: str | None
    params: NotRequired[str | None]
    results: list[CATEGORY_T]


class Thumbnail(TypedDict):
    url: str
    width: int
    height: int


class ArtistInfo(TypedDict):
    id: str | None
    name: str | None


class AlbumInfo(TypedDict):
    title: str
    type: str
    artists: list[ArtistInfo]
    browseId: str
    audioPlaylistId: str | None
    thumbnails: list[Thumbnail]
    isExplicit: bool
    year: NotRequired[str]


class SingleInfo(TypedDict):
    title: str
    year: str | None
    browseId: str
    thumbnails: list[Thumbnail]


class VideoInfo(TypedDict):
    title: str
    videoId: str
    artists: list[ArtistInfo]
    playlistId: str | None
    thumbnails: list[Thumbnail] | None
    views: str


class PlaylistInfo(TypedDict):
    title: str | None
    playlistId: str
    thumbnails: list[Thumbnail]
    description: NotRequired[str]
    count: NotRequired[str]
    author: NotRequired[list[ArtistInfo]]


class RelatedArtistInfo(TypedDict):
    title: str
    browseId: str
    subscribers: str | None
    thumbnails: list[Thumbnail]


class EpisodeInfo(TypedDict):
    index: str | None
    title: str
    description: str | None
    duration: str | None
    videoId: str | None
    browseId: str | None
    videoType: str | None
    date: str | None
    thumbnails: list[Thumbnail]


class PodcastInfo(TypedDict):
    title: str
    channel: ArtistInfo
    browseId: str
    podcastId: str | None
    thumbnails: list[Thumbnail]


class BaseResourceInfo(TypedDict):
    albums: CategoryDict[AlbumInfo]
    singles: CategoryDict[SingleInfo]
    shows: CategoryDict[AlbumInfo]
    videos: CategoryDict[VideoInfo]
    playlists: CategoryDict[PlaylistInfo]
    related: CategoryDict[RelatedArtistInfo]
    episodes: CategoryDict[EpisodeInfo]
    podcasts: CategoryDict[PodcastInfo]


class AlbumDict(TypedDict):
    name: str
    id: str | None


class PinData(TypedDict):
    pin: str | None
    unpin: str | None


class AddRemoveData(TypedDict):
    add: str | None
    remove: str | None


class SongMenuData(TypedDict):
    inLibrary: NotRequired[bool]
    pinnedToListenAgain: NotRequired[bool | None]
    listenAgainFeedbackTokens: NotRequired[PinData]
    feedbackTokens: NotRequired[AddRemoveData]
    feedbackToken: NotRequired[str | None]


class PlaylistItem(TypedDict):
    videoId: str | None
    title: str | None
    artists: list[ArtistInfo] | None
    album: AlbumDict | None
    likeStatus: str | None
    thumbnails: list[Thumbnail] | None
    isAvailable: bool
    isExplicit: bool
    videoType: str | None
    views: str | None

    in_library: bool | None
    pinnedToListenAgain: bool | None
    listenAgainFeedbackTokens: NotRequired[PinData]
    feedbackTokens: NotRequired[AddRemoveData]
    feedbackToken: NotRequired[str | None]

    trackNumber: NotRequired[int | None]
    duration: NotRequired[str]
    duration_seconds: NotRequired[int | None]
    setVideoId: NotRequired[str]


class SongsDict(TypedDict):
    browseId: str | None
    results: NotRequired[list[PlaylistItem]]


class ArtistResourceInfo(BaseResourceInfo):
    name: str
    description: str | None
    views: str | None
    channelId: str
    shuffleId: str | None
    radioId: str | None
    subscribers: str | None
    monthlyListeners: str | None
    subscribed: bool
    thumbnails: list[Thumbnail]
    songs: SongsDict


class UserResourceInfo(BaseResourceInfo):
    name: str


class ChannelResourceInfo(BaseResourceInfo):
    title: str
    thumbnails: list[Thumbnail]
