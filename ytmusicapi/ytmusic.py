import gettext
import os
import time
from contextlib import suppress
from functools import partial
from typing import Dict, Optional

import requests
from requests.structures import CaseInsensitiveDict

from ytmusicapi.helpers import *
from ytmusicapi.mixins.browsing import BrowsingMixin
from ytmusicapi.mixins.explore import ExploreMixin
from ytmusicapi.mixins.library import LibraryMixin
from ytmusicapi.mixins.playlists import PlaylistsMixin
from ytmusicapi.mixins.search import SearchMixin
from ytmusicapi.mixins.uploads import UploadsMixin
from ytmusicapi.mixins.watch import WatchMixin
from ytmusicapi.parsers.i18n import Parser

from .auth.oauth import OAuthCredentials, OAuthToken, RefreshingToken
from .auth.oauth.base import Token
from .auth.types import AuthType


class YTMusic(
    BrowsingMixin, SearchMixin, WatchMixin, ExploreMixin, LibraryMixin, PlaylistsMixin, UploadsMixin
):
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """

    def __init__(
        self,
        auth: Optional[str | Dict] = None,
        user: str = None,
        requests_session=True,
        proxies: Dict = None,
        language: str = "en",
        location: str = "",
        oauth_credentials: Optional[OAuthCredentials] = None,
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
        :param requests_session: A Requests session object or a truthy value to create one.
          Default sessions have a request timeout of 30s, which produces a requests.exceptions.ReadTimeout.
          The timeout can be changed by passing your own Session object::

            s = requests.Session()
            s.request = functools.partial(s.request, timeout=3)
            ytm = YTMusic(requests_session=s)

          A falsy value disables sessions.
          It is generally a good idea to keep sessions enabled for
          performance reasons (connection pooling).
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

        self._base_headers = None  #: for authless initializing requests during OAuth flow
        self._headers = None  #: cache formed headers including auth

        self.auth = auth  #: raw auth
        self._input_dict = {}  #: parsed auth arg value in dictionary format

        self.auth_type: AuthType = AuthType.UNAUTHORIZED

        self._token: Token  #: OAuth credential handler
        self.oauth_credentials: OAuthCredentials  #: Client used for OAuth refreshing

        self._session: requests.Session  #: request session for connection pooling
        self.proxies: Dict = proxies  #: params for session modification

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
                self._session.request = partial(self._session.request, timeout=30)
            else:  # Use the Requests API module as a "session".
                self._session = requests.api

        # see google cookie docs: https://policies.google.com/technologies/cookies
        # value from https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/youtube.py#L502
        self.cookies = {"SOCS": "CAI"}
        if self.auth is not None:
            self.oauth_credentials = (
                oauth_credentials if oauth_credentials is not None else OAuthCredentials()
            )
            auth_filepath = None
            if isinstance(self.auth, str):
                if os.path.isfile(auth):
                    with open(auth) as json_file:
                        auth_filepath = auth
                        input_json = json.load(json_file)
                else:
                    input_json = json.loads(auth)
                self._input_dict = CaseInsensitiveDict(input_json)

            else:
                self._input_dict = self.auth

            if OAuthToken.is_oauth(self._input_dict):
                base_token = OAuthToken(**self._input_dict)
                self._token = RefreshingToken(base_token, self.oauth_credentials, auth_filepath)
                self.auth_type = AuthType.OAUTH_CUSTOM_CLIENT if oauth_credentials else AuthType.OAUTH_DEFAULT

        # prepare context
        self.context = initialize_context()

        if location:
            if location not in SUPPORTED_LOCATIONS:
                raise Exception("Location not supported. Check the FAQ for supported locations.")
            self.context["context"]["client"]["gl"] = location

        if language not in SUPPORTED_LANGUAGES:
            raise Exception(
                "Language not supported. Supported languages are " + (", ".join(SUPPORTED_LANGUAGES)) + "."
            )
        self.context["context"]["client"]["hl"] = language
        self.language = language
        try:
            locale.setlocale(locale.LC_ALL, self.language)
        except locale.Error:
            with suppress(locale.Error):
                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

        locale_dir = os.path.abspath(os.path.dirname(__file__)) + os.sep + "locales"
        self.lang = gettext.translation("base", localedir=locale_dir, languages=[language])
        self.parser = Parser(self.lang)

        if user:
            self.context["context"]["user"]["onBehalfOfUser"] = user

        auth_headers = self._input_dict.get("authorization")
        if auth_headers:
            if "SAPISIDHASH" in auth_headers:
                self.auth_type = AuthType.BROWSER
            elif auth_headers.startswith("Bearer"):
                self.auth_type = AuthType.OAUTH_CUSTOM_FULL

        # sapsid, origin, and params all set once during init
        self.params = YTM_PARAMS
        if self.auth_type == AuthType.BROWSER:
            self.params += YTM_PARAMS_KEY
            try:
                cookie = self.base_headers.get("cookie")
                self.sapisid = sapisid_from_cookie(cookie)
                self.origin = self.base_headers.get("origin", self.base_headers.get("x-origin"))
            except KeyError:
                raise Exception("Your cookie is missing the required value __Secure-3PAPISID")

    @property
    def base_headers(self):
        if not self._base_headers:
            if self.auth_type == AuthType.BROWSER or self.auth_type == AuthType.OAUTH_CUSTOM_FULL:
                self._base_headers = self._input_dict
            else:
                self._base_headers = {
                    "user-agent": USER_AGENT,
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate",
                    "content-type": "application/json",
                    "content-encoding": "gzip",
                    "origin": YTM_DOMAIN,
                }

        return self._base_headers

    @property
    def headers(self):
        # set on first use
        if not self._headers:
            self._headers = self.base_headers

        # keys updated each use, custom oauth implementations left untouched
        if self.auth_type == AuthType.BROWSER:
            self._headers["authorization"] = get_authorization(self.sapisid + " " + self.origin)

        elif self.auth_type in AuthType.oauth_types():
            self._headers["authorization"] = self._token.as_auth()
            self._headers["X-Goog-Request-Time"] = str(int(time.time()))

        return self._headers

    def _send_request(self, endpoint: str, body: Dict, additionalParams: str = "") -> Dict:
        body.update(self.context)

        # only required for post requests (?)
        if "X-Goog-Visitor-Id" not in self.headers:
            self._headers.update(get_visitor_id(self._send_get_request))

        response = self._session.post(
            YTM_BASE_API + endpoint + self.params + additionalParams,
            json=body,
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        )
        response_text = json.loads(response.text)
        if response.status_code >= 400:
            message = "Server returned HTTP " + str(response.status_code) + ": " + response.reason + ".\n"
            error = response_text.get("error", {}).get("message")
            raise Exception(message + error)
        return response_text

    def _send_get_request(self, url: str, params: Dict = None):
        response = self._session.get(
            url,
            params=params,
            # handle first-use x-goog-visitor-id fetching
            headers=self.headers if self._headers else self.base_headers,
            proxies=self.proxies,
            cookies=self.cookies,
        )
        return response

    def _check_auth(self):
        if not self.auth:
            raise Exception("Please provide authentication before using this function")

    def __enter__(self):
        return self

    def __exit__(self, execType=None, execValue=None, trackback=None):
        pass
