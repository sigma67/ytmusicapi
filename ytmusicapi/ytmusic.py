import requests
import gettext
import os
from functools import partial
from contextlib import suppress
from typing import Dict

from requests.structures import CaseInsensitiveDict
from ytmusicapi.auth.headers import load_headers_file, prepare_headers
from ytmusicapi.parsers.i18n import Parser
from ytmusicapi.helpers import *
from ytmusicapi.mixins.browsing import BrowsingMixin
from ytmusicapi.mixins.search import SearchMixin
from ytmusicapi.mixins.watch import WatchMixin
from ytmusicapi.mixins.explore import ExploreMixin
from ytmusicapi.mixins.library import LibraryMixin
from ytmusicapi.mixins.playlists import PlaylistsMixin
from ytmusicapi.mixins.uploads import UploadsMixin
from ytmusicapi.auth.oauth import YTMusicOAuth, is_oauth


class YTMusic(BrowsingMixin, SearchMixin, WatchMixin, ExploreMixin, LibraryMixin, PlaylistsMixin,
              UploadsMixin):
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """

    def __init__(self,
                 auth: str = None,
                 user: str = None,
                 requests_session=True,
                 proxies: dict = None,
                 language: str = 'en',
                 location: str = ''):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide a string or path to file.
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
            ytm = YTMusic(session=s)

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
        """
        self.auth = auth
        self.input_dict = None
        self.is_oauth_auth = False

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
                self._session.request = partial(self._session.request, timeout=30)
            else:  # Use the Requests API module as a "session".
                self._session = requests.api

        self.proxies = proxies
        self.cookies = {'CONSENT': 'YES+1'}
        if self.auth is not None:
            input_json = load_headers_file(self.auth)
            self.input_dict = CaseInsensitiveDict(input_json)
            self.input_dict['filepath'] = self.auth
            self.is_oauth_auth = is_oauth(self.input_dict)

        self.headers = prepare_headers(self._session, proxies, self.input_dict)

        if 'x-goog-visitor-id' not in self.headers:
            self.headers.update(get_visitor_id(self._send_get_request))

        # prepare context
        self.context = initialize_context()

        if location:
            if location not in SUPPORTED_LOCATIONS:
                raise Exception("Location not supported. Check the FAQ for supported locations.")
            self.context['context']['client']['gl'] = location

        if language not in SUPPORTED_LANGUAGES:
            raise Exception("Language not supported. Supported languages are "
                            + (', '.join(SUPPORTED_LANGUAGES)) + ".")
        self.context['context']['client']['hl'] = language
        self.language = language
        try:
            locale.setlocale(locale.LC_ALL, self.language)
        except locale.Error:
            with suppress(locale.Error):
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        locale_dir = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'locales'
        self.lang = gettext.translation('base', localedir=locale_dir, languages=[language])
        self.parser = Parser(self.lang)

        if user:
            self.context['context']['user']['onBehalfOfUser'] = user

        auth_header = self.headers.get("authorization")
        self.is_browser_auth = auth_header and "SAPISIDHASH" in auth_header
        if self.is_browser_auth:
            try:
                cookie = self.headers.get('cookie')
                self.sapisid = sapisid_from_cookie(cookie)
            except KeyError:
                raise Exception("Your cookie is missing the required value __Secure-3PAPISID")



    def _send_request(self, endpoint: str, body: Dict, additionalParams: str = "") -> Dict:

        if self.is_oauth_auth:
            self.headers = prepare_headers(self._session, self.proxies, self.input_dict) 
        body.update(self.context)
        params = YTM_PARAMS
        if self.is_browser_auth:
            origin = self.headers.get('origin', self.headers.get('x-origin'))
            self.headers["authorization"] = get_authorization(self.sapisid + ' ' + origin)
            params += YTM_PARAMS_KEY

        response = self._session.post(YTM_BASE_API + endpoint + params + additionalParams,
                                      json=body,
                                      headers=self.headers,
                                      proxies=self.proxies,
                                      cookies=self.cookies)
        response_text = json.loads(response.text)
        if response.status_code >= 400:
            message = "Server returned HTTP " + str(
                response.status_code) + ": " + response.reason + ".\n"
            error = response_text.get('error', {}).get('message')
            raise Exception(message + error)
        return response_text

    def _send_get_request(self, url: str, params: Dict = None):
        response = self._session.get(url,
                                     params=params,
                                     headers=self.headers,
                                     proxies=self.proxies,
                                     cookies=self.cookies)
        return response

    def _check_auth(self):
        if not self.auth:
            raise Exception("Please provide authentication before using this function")

    def __enter__(self):
        return self

    def __exit__(self, execType=None, execValue=None, trackback=None):
        pass
