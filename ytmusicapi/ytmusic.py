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

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict

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


class YTMusicBase:
    def __init__(
        self,
        auth: str | JsonDict | None = None,
        user: str | None = None,
        requests_session: requests.Session | None = None,
        proxies: dict[str, str] | None = None,
        language: str = "en",
        location: str = "",
        oauth_credentials: OAuthCredentials | None = None,
    ):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide a string, path to file, or oauth token dict.
          Authentication credentials are needed to manage your library.
          See :py:func:`setup` for how to fill in the correct credentials.
          Default: A default header is used without authentication.
        :param user: Optional. Specify a user ID string to use in requests.
          This is needed if you want to send requests on behalf of a brand account.
          Otherwise the default account is used. You can retrieve the user ID
          by going to https://myaccount.google.com/brandaccounts and selecting your brand account.
          The user ID will be in the URL: https://myaccount.google.com/b/user_id/
        :param requests_session: A Requests session object or None to create one.
          Default sessions have a request timeout of 30s, which produces a requests.exceptions.ReadTimeout.
          The timeout can be changed by passing your own Session object::

            s = requests.Session()
            s.request = functools.partial(s.request, timeout=3)
            ytm = YTMusic(requests_session=s)

        :param proxies: Optional. Proxy configuration in requests_ format_.

            .. _requests: https://requests.readthedocs.io/
            .. _format: https://requests.readthedocs.io/en/master/user/advanced/#proxies

        :param language: Optional. Can be used to change the language of returned data.
            English will be used by default. Available languages can be checked in
            the ytmusicapi/locales directory.
        :param location: Optional. Can be used to change the location of the user.
            No location will be set by default. This means it is determined by the server.
            Available languages can be checked in the FAQ.
        :param oauth_credentials: Optional. Used to specify a different oauth client to be
            used for authentication flow.
        """
        #: request session for connection pooling
        self._session = self._prepare_session(requests_session)
        self.proxies: dict[str, str] | None = proxies  #: params for session modification
        # see google cookie docs: https://policies.google.com/technologies/cookies
        # value from https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/youtube.py#L502
        self.cookies = {"SOCS": "CAI"}

        self._auth_headers: CaseInsensitiveDict[str] = CaseInsensitiveDict[str]()
        self.auth_type = AuthType.UNAUTHORIZED
        if auth is not None:
            self._auth_headers, auth_path = parse_auth_str(auth)
            self.auth_type = determine_auth_type(self._auth_headers)

            self._token: Token
            if self.auth_type == AuthType.OAUTH_CUSTOM_CLIENT:
                if oauth_credentials is None:
                    raise YTMusicUserError(
                        "oauth JSON provided via auth argument, but oauth_credentials not provided."
                        "Please provide oauth_credentials as specified in the OAuth setup documentation."
                    )
                #: OAuth credential handler
                self._token = RefreshingToken(
                    credentials=oauth_credentials, _local_cache=auth_path, **self._auth_headers
                )

        # prepare context
        self.context = initialize_context()

        if location:
            if location not in SUPPORTED_LOCATIONS:
                raise YTMusicUserError("Location not supported. Check the FAQ for supported locations.")
            self.context["context"]["client"]["gl"] = location

        if language not in SUPPORTED_LANGUAGES:
            raise YTMusicUserError(
                "Language not supported. Supported languages are " + (", ".join(SUPPORTED_LANGUAGES)) + "."
            )
        self.context["context"]["client"]["hl"] = language
        self.language = language
        try:
            locale.setlocale(locale.LC_ALL, self.language)
        except locale.Error:
            with suppress(locale.Error):
                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

        locale_dir = Path(__file__).parent.resolve() / "locales"
        self.lang = gettext.translation("base", localedir=locale_dir, languages=[language])
        self.parser = Parser(self.lang)

        if user:
            self.context["context"]["user"]["onBehalfOfUser"] = user

        # sapisid, origin, and params all set once during init
        self.params = YTM_PARAMS
        if self.auth_type == AuthType.BROWSER:
            self.params += YTM_PARAMS_KEY
            try:
                cookie = self.base_headers["cookie"]
                self.sapisid = sapisid_from_cookie(cookie)
                self.origin: str = self.base_headers.get("origin", str(self.base_headers.get("x-origin")))
            except KeyError:
                raise YTMusicUserError("Your cookie is missing the required value __Secure-3PAPISID")

    @cached_property
    def base_headers(self) -> CaseInsensitiveDict[str]:
        headers = (
            self._auth_headers
            if self.auth_type == AuthType.BROWSER or self.auth_type == AuthType.OAUTH_CUSTOM_FULL
            else initialize_headers()
        )

        if "X-Goog-Visitor-Id" not in headers:
            headers.update(get_visitor_id(partial(self._send_get_request, use_base_headers=True)))

        return headers

    @property
    def headers(self) -> CaseInsensitiveDict[str]:
        headers = self.base_headers

        # keys updated each use, custom oauth implementations left untouched
        if self.auth_type == AuthType.BROWSER:
            headers["authorization"] = get_authorization(self.sapisid + " " + self.origin)

        # Do not set custom headers when using OAUTH_CUSTOM_FULL
        # Full headers are provided by the downstream client in this scenario.
        elif self.auth_type == AuthType.OAUTH_CUSTOM_CLIENT:
            headers["authorization"] = self._token.as_auth()
            headers["X-Goog-Request-Time"] = str(int(time.time()))

        return headers

    @contextmanager
    def as_mobile(self) -> Iterator[None]:
        """
        Not thread-safe!
        ----------------

        Temporarily changes the `context` to enable different results
        from the API, meant for the Android mobile-app.
        All calls inside the `with`-statement with emulate mobile behavior.

        This context-manager has no `enter_result`, as it operates in-place
        and only temporarily alters the underlying `YTMusic`-object.


        Example::

            with yt.as_mobile():
                yt._send_request(...)  # results as mobile-app

            yt._send_request(...)  # back to normal, like web-app

        """

        # change the context to emulate a mobile-app (Android)
        copied_context_client = self.context["context"]["client"].copy()
        self.context["context"]["client"].update({"clientName": "ANDROID_MUSIC", "clientVersion": "7.21.50"})

        # this will not catch errors
        try:
            yield None
        finally:
            # safely restore the old context
            self.context["context"]["client"] = copied_context_client

    def _prepare_session(self, requests_session: requests.Session | None) -> requests.Session:
        """Prepare requests session or use user-provided requests_session"""
        if isinstance(requests_session, requests.Session):
            return requests_session
        self._session = requests.Session()
        self._session.request = partial(self._session.request, timeout=30)  # type: ignore[method-assign]
        return self._session

    def _send_request(self, endpoint: str, body: JsonDict, additionalParams: str = "") -> JsonDict:
        body.update(self.context)

        response = self._session.post(
            YTM_BASE_API + endpoint + self.params + additionalParams,
            json=body,
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        )
        response_text: JsonDict = json.loads(response.text)
        if response.status_code >= 400:
            message = "Server returned HTTP " + str(response.status_code) + ": " + response.reason + ".\n"
            error = response_text.get("error", {}).get("message")
            raise YTMusicServerError(message + error)
        return response_text

    def _send_get_request(
        self, url: str, params: JsonDict | None = None, use_base_headers: bool = False
    ) -> Response:
        response = self._session.get(
            url,
            params=params,
            # handle first-use x-goog-visitor-id fetching
            headers=initialize_headers() if use_base_headers else self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        )
        return response

    def _check_auth(self) -> None:
        """
        Checks if the user has provided authorization credentials

        Raises:
            YTMusicUserError: if the user is not authorized
        """
        if self.auth_type == AuthType.UNAUTHORIZED:
            raise YTMusicUserError("Please provide authentication before using this function")

    def __enter__(self) -> YTMusicBase:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any | None,
    ) -> bool | None:
        pass


class YTMusic(
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
