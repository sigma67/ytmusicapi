from ..base import YTMusicModel


class Thumbnail(YTMusicModel):
    url: str
    width: int | None = None
    height: int | None = None


class _NamedRef(YTMusicModel):
    name: str | None = None
    id: str | None = None


class ArtistRef(_NamedRef):
    pass


class AlbumRef(_NamedRef):
    pass


class PlaylistRef(YTMusicModel):
    shuffleId: str | None = None
    radioId: str | None = None


class FeedbackTokens(YTMusicModel):
    add: str | None = None
    remove: str | None = None
