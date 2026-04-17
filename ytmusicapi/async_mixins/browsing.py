import re
import warnings
from typing import Any, Literal, overload
from ytmusicapi.continuations import get_continuations, get_reloadable_continuation_params
from ytmusicapi.helpers import YTM_DOMAIN, sum_total_duration
from ytmusicapi.models.lyrics import LyricLine, Lyrics, TimedLyrics
from ytmusicapi.parsers.albums import parse_album_header_2024
from ytmusicapi.parsers.browsing import parse_album, parse_content_list, parse_mixed_content, parse_playlist, parse_video
from ytmusicapi.parsers.library import parse_albums
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType
from ..exceptions import YTMusicError, YTMusicUserError
from ..navigation import *
from ._protocol import MixinProtocol
from ytmusicapi.mixins._utils import get_datestamp

class BrowsingMixin(MixinProtocol):

    async def get_home(self, limit: int=3) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_artist(self, channelId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass
    ArtistOrderType = Literal['Recency', 'Popularity', 'Alphabetical order']

    async def get_artist_albums(self, channelId: str, params: str, limit: int | None=100, order: ArtistOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_user(self, channelId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_user_playlists(self, channelId: str, params: str) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_user_videos(self, channelId: str, params: str) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_album_browse_id(self, audioPlaylistId: str) -> str | None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_album(self, browseId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_song(self, videoId: str, signatureTimestamp: int | None=None) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_song_related(self, browseId: str) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    @overload
    async def get_lyrics(self, browseId: str, timestamps: Literal[False]=False) -> Lyrics | None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    @overload
    async def get_lyrics(self, browseId: str, timestamps: Literal[True]=True) -> Lyrics | TimedLyrics | None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_lyrics(self, browseId: str, timestamps: bool | None=False) -> Lyrics | TimedLyrics | None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_basejs_url(self) -> str:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_signatureTimestamp(self, url: str | None=None) -> int:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def get_tasteprofile(self) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass

    async def set_tasteprofile(self, artists: list[str], taste_profile: JsonDict | None=None) -> None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/browsing.py"""
        pass