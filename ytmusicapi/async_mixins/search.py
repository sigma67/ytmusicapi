from ytmusicapi.continuations import get_continuations
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.search import *
from ytmusicapi.type_alias import JsonList, ParseFuncType, RequestFuncType

class SearchMixin(MixinProtocol):

    async def search(self, query: str, filter: str | None=None, scope: str | None=None, limit: int=20, ignore_spelling: bool=False) -> JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/search.py"""
        pass

    async def get_search_suggestions(self, query: str, detailed_runs: bool=False) -> list[str] | JsonList:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/search.py"""
        pass

    async def remove_search_suggestions(self, suggestions: JsonList, indices: list[int] | None=None) -> bool:
        """Original reference: https://github.com/sigma67/ytmusicapi/blob/a8a120f37c5363ffb4d36d226c1afb2051bd4d79/ytmusicapi/mixins/search.py"""
        pass