from ytmusicapi.continuations import *
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.navigation import *
from ytmusicapi.parsers.browsing import parse_content_list
from ytmusicapi.parsers.playlists import parse_playlist_header
from ytmusicapi.parsers.podcasts import *
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType
from ytmusicapi.mixins._utils import *

class PodcastsMixin(MixinProtocol):
    """Podcasts Mixin"""

    async def get_channel(self, channelId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/podcasts.py"""
        pass

    async def get_channel_episodes(self, channelId: str, params: str) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/podcasts.py"""
        pass

    async def get_podcast(self, playlistId: str, limit: int | None=100) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/podcasts.py"""
        pass

    async def get_episode(self, videoId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/podcasts.py"""
        pass

    async def get_episodes_playlist(self, playlist_id: str='RDPN') -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/podcasts.py"""
        pass