import typing
from pathlib import Path
import requests
from ytmusicapi.continuations import get_continuations
from ytmusicapi.helpers import *
from ytmusicapi.navigation import *
from ytmusicapi.parsers.albums import parse_album_header
from ytmusicapi.parsers.library import get_library_contents, parse_library_albums, parse_library_artists, pop_songs_random_mix
from ytmusicapi.parsers.uploads import parse_uploaded_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType
from ..auth.types import AuthType
from ..enums import ResponseStatus
from ..exceptions import YTMusicUserError
from ._protocol import MixinProtocol
from ytmusicapi.mixins._utils import LibraryOrderType, prepare_order_params, validate_order_parameter

class UploadsMixin(MixinProtocol):

    async def get_library_upload_songs(self, limit: int | None=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def get_library_upload_albums(self, limit: int | None=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def get_library_upload_artists(self, limit: int | None=25, order: LibraryOrderType | None=None) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def get_library_upload_artist(self, browseId: str, limit: int=25) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def get_library_upload_album(self, browseId: str) -> JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def upload_song(self, filepath: str) -> ResponseStatus | requests.Response:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass

    async def delete_upload_entity(self, entityId: str) -> str | JsonDict:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/uploads.py"""
        pass