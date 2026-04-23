from ytmusicapi.continuations import *
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.helpers import sum_total_duration
from ytmusicapi.navigation import *
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist
from ytmusicapi.parsers.playlists import *
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncBodyType, RequestFuncType
from ._protocol import MixinProtocol
from ytmusicapi.mixins._utils import *

class PlaylistsMixin(MixinProtocol):

    async def get_playlist(self, playlistId: str, limit: int | None=100, related: bool=False, suggestions_limit: int=0) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def get_liked_songs(self, limit: int=100) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def get_saved_episodes(self, limit: int=100) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def create_playlist(self, title: str, description: str, privacy_status: str='PRIVATE', video_ids: list[str] | None=None, source_playlist: str | None=None) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def edit_playlist(self, playlistId: str, title: str | None=None, description: str | None=None, privacyStatus: str | None=None, moveItem: str | tuple[str, str] | None=None, addPlaylistId: str | None=None, addToTop: bool | None=None) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def delete_playlist(self, playlistId: str) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def add_playlist_items(self, playlistId: str, videoIds: list[str] | None=None, source_playlist: str | None=None, duplicates: bool=False) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass

    async def remove_playlist_items(self, playlistId: str, videos: JsonList) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/playlists.py"""
        pass