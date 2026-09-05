"""Response models for the upload-library methods.

Uploaded items are similar to but not the same as regular songs: they carry an
``entityId`` and lack several fields YTM-hosted songs have. Until the song model
from #983 and the shared leaf models from #981 land, the shapes are modelled
here; the leaves deliberately match #981 so they can be re-homed onto the
shared models without touching callers.
"""

from .base import YTMusicModel
from .content.enums import LikeStatus


class Thumbnail(YTMusicModel):
    url: str
    width: int | None = None
    height: int | None = None


class ArtistRef(YTMusicModel):
    name: str | None = None
    id: str | None = None


class AlbumRef(YTMusicModel):
    name: str | None = None
    id: str | None = None


class UploadSong(YTMusicModel):
    """An uploaded song, as returned by the upload-library methods."""

    entityId: str
    videoId: str
    title: str | None = None
    duration: str | None = None
    duration_seconds: int | None = None
    artists: list[ArtistRef]
    album: AlbumRef | None = None
    likeStatus: LikeStatus
    thumbnails: list[Thumbnail] | None = None


class UploadAlbum(YTMusicModel):
    """An uploaded album with its tracks, as returned by ``get_library_upload_album``."""

    title: str
    type: str
    thumbnails: list[Thumbnail] | None = None
    isExplicit: bool
    description: str | None = None
    artists: list[ArtistRef] | None = None
    year: str | None = None
    trackCount: int | None = None
    duration: str
    audioPlaylistId: str | None = None
    likeStatus: LikeStatus | None = None
    tracks: list[UploadSong]
    duration_seconds: int
