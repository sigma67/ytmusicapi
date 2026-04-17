from __future__ import annotations

import gettext
import json
import locale
import time
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from functools import cached_property, partial
from pathlib import Path
from typing import Any

import httpx 

from ytmusicapi.helpers import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_LOCATIONS,
    YTM_BASE_API,
    YTM_PARAMS,
    YTM_PARAMS_KEY,
    get_authorization,
    get_visitor_id,
    initialize_context,
    initialize_headers,
    sapisid_from_cookie,
)
from ytmusicapi.mixins.browsing import BrowsingMixin
from ytmusicapi.mixins.charts import ChartsMixin
from ytmusicapi.mixins.explore import ExploreMixin
from ytmusicapi.mixins.library import LibraryMixin
from ytmusicapi.mixins.playlists import PlaylistsMixin
from ytmusicapi.mixins.podcasts import PodcastsMixin
from ytmusicapi.mixins.search import SearchMixin
from ytmusicapi.mixins.uploads import UploadsMixin
from ytmusicapi.mixins.watch import WatchMixin
from ytmusicapi.parsers.i18n import Parser

from .auth.auth_parse import determine_auth_type, parse_auth_str
from .auth.oauth import OAuthCredentials, RefreshingToken
from .auth.oauth.token import Token
from .auth.types import AuthType
from .exceptions import YTMusicServerError, YTMusicUserError
from .type_alias import JsonDict

from .ytmusic import YTMusicBase 

class AsyncYTMusicBase(YTMusicBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    async def base_headers(self) -> CaseInsensitiveDict[str]:
        headers = (
            self._auth_headers
            if self.auth_type == AuthType.BROWSER or self.auth_type == AuthType.OAUTH_CUSTOM_FULL
            else initialize_headers()
        )
        #Dont see the point of rewriting an async version of get_visitor_id if its only used once here?
        if "X-Goog-Visitor-Id" not in headers:
            response = await self._send_get_request(YTM_DOMAIN, use_base_headers=True)
            matches = re.findall(r"ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;", response.text)
            visitor_id = ""
            if len(matches) > 0:
                ytcfg = json.loads(matches[0])
                visitor_id = ytcfg.get("VISITOR_DATA")

            headers.update({"X-Goog-Visitor-Id": visitor_id})

        return headers

    def _prepare_session(self, async_client: httpx.AsyncClient | None) -> requests.Session:
        """
            Prepare a httpx AsyncClient or use the user-provided client
            Note httpx async client cannot change the proxy per request similar to the requests module in order to change the module will need to destroy old object and create a new one
        """
        if isinstance(async_client, httpx.AsyncClient):
            return async_client

        self._session = httpx.AsyncClient(timeout=30.0, proxy=self.proxies)
        return self._session

    async def _send_request(self, endpoint: str, body: JsonDict, additionalParams: str = "") -> JsonDict:
        body.update(self.context)

        response = await self._session.post(
            YTM_BASE_API + endpoint + self.params + additionalParams,
            json=body,
            headers=self.headers,
            cookies=self.cookies,
        )
        response_text: JsonDict = response.json()
        if response.status_code >= 400:
            message = "Server returned HTTP " + str(response.status_code) + ": " + response.reason + ".\n"
            error = response_text.get("error", {}).get("message")
            raise YTMusicServerError(message + error)
        return response_text

    async def _send_get_request(
        self, url: str, params: JsonDict | None = None, use_base_headers: bool = False
    ) -> Response:
        response = await self._session.get(
            url,
            params=params,
            # handle first-use x-goog-visitor-id fetching
            headers=initialize_headers() if use_base_headers else self.headers,
            cookies=self.cookies,
        )
        return response

    def __enter__(self) -> YTMusicBase:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any | None,
    ) -> bool | None:
        pass


class AsyncYTMusic(
    YTMusicBase,
    BrowsingMixin,
    SearchMixin,
    WatchMixin,
    ChartsMixin,
    ExploreMixin,
    LibraryMixin,
    PlaylistsMixin,
    PodcastsMixin,
    UploadsMixin,
):
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """
