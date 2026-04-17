from collections.abc import Callable
from random import randint
from requests import Response
from ytmusicapi.continuations import *
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.library import *
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncDictType, ParseFuncType, RequestFuncType
from ..exceptions import YTMusicServerError
from ._protocol import MixinProtocol
from ytmusicapi.mixins._utils import *

class LibraryMixin(MixinProtocol):

    async def get_library_playlists(self, limit: int | None=25) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_songs(self, limit: int=25, validate_responses: bool=False, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_albums(self, limit: int=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_artists(self, limit: int=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_subscriptions(self, limit: int=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_podcasts(self, limit: int=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_library_channels(self, limit: int=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_history(self) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def add_history_item(self, song: JsonDict) -> Response:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def remove_history_items(self, feedbackTokens: list[str]) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def rate_song(self, videoId: str, rating: LikeStatus=LikeStatus.INDIFFERENT) -> JsonDict | None:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def edit_song_library_status(self, feedbackTokens: list[str] | None=None) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def rate_playlist(self, playlistId: str, rating: LikeStatus=LikeStatus.INDIFFERENT) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def subscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def unsubscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass

    async def get_account_info(self) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/library.py"""
        pass