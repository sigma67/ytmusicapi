from ytmusicapi.continuations import get_continuations
from ytmusicapi.exceptions import YTMusicServerError, YTMusicUserError
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.playlists import validate_playlist_id
from ytmusicapi.parsers.watch import *
from ytmusicapi.type_alias import JsonList, ParseFuncType, RequestFuncType

class WatchMixin(MixinProtocol):

    async def get_watch_playlist(self, videoId: str | None=None, playlistId: str | None=None, limit: int=25, radio: bool=False, shuffle: bool=False) -> dict[str, JsonList | str | None]:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/watch.py"""
        pass