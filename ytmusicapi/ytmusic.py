import requests
import json
import gettext
import pkg_resources
import os
from contextlib import suppress
from typing import Dict
from ytmusicapi.helpers import *
from ytmusicapi.parsers import browsing
from ytmusicapi.setup import setup
from ytmusicapi.mixins.browsing import BrowsingMixin
from ytmusicapi.mixins.watch import WatchMixin
from ytmusicapi.mixins.library import LibraryMixin
from ytmusicapi.mixins.playlists import PlaylistsMixin
from ytmusicapi.mixins.uploads import UploadsMixin

params = '?alt=json&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
base_url = 'https://music.youtube.com/youtubei/v1/'


class YTMusic(BrowsingMixin, WatchMixin, LibraryMixin, PlaylistsMixin, UploadsMixin):
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
                 language: str = 'en'):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide a string or path to file.
          Authentication credentials are needed to manage your library.
          Should be an adjusted version of `headers_auth.json.example` in the project root.
          See :py:func:`setup` for how to fill in the correct credentials.
          Default: A default header is used without authentication.
        :param user: Optional. Specify a user ID string to use in requests.
          This is needed if you want to send requests on behalf of a brand account.
          Otherwise the default account is used. You can retrieve the user ID
          by going to https://myaccount.google.com/brandaccounts and selecting your brand account.
          The user ID will be in the URL: https://myaccount.google.com/b/user_id/
        :param requests_session: A Requests session object or a truthy value to create one.
          A falsy value disables sessions.
          It is generally a good idea to keep sessions enabled for
          performance reasons (connection pooling).
        :param proxies: Optional. Proxy configuration in requests_ format_.

            .. _requests: https://requests.readthedocs.io/
            .. _format: https://requests.readthedocs.io/en/master/user/advanced/#proxies

        :param language: Optional. Can be used to change the language of returned data.
            English will be used by default. Available languages can be checked in
            the ytmusicapi/locales directory.
        """
        self.auth = auth

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                self._session = requests.api

        self.proxies = proxies

        try:
            if auth is None or os.path.isfile(auth):
                file = auth if auth else pkg_resources.resource_filename(
                    'ytmusicapi', 'headers.json')
                with open(file) as json_file:
                    self.headers = json.load(json_file)
            else:
                self.headers = json.loads(auth)
        except Exception as e:
            print(
                "Failed loading provided credentials. Make sure to provide a string or a file path. "
                "Reason: " + str(e))

        with open(pkg_resources.resource_filename('ytmusicapi', 'context.json')) as json_file:
            self.context = json.load(json_file)

        self.context['context']['client']['hl'] = language
        supported_languages = [f for f in pkg_resources.resource_listdir('ytmusicapi', 'locales')]
        if language not in supported_languages:
            raise Exception("Language not supported. Supported languages are "
                            ', '.join(supported_languages))
        self.language = language
        try:
            locale.setlocale(locale.LC_ALL, self.language)
        except locale.Error:
            with suppress(locale.Error):
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.lang = gettext.translation('base',
                                        localedir=pkg_resources.resource_filename(
                                            'ytmusicapi', 'locales'),
                                        languages=[language])
        self.parser = browsing.Parser(self.lang)

        if user:
            self.context['context']['user']['onBehalfOfUser'] = user

        # verify authentication credentials work
        if auth:
            try:
                self.sapisid = sapisid_from_cookie(self.headers['Cookie'])
            except KeyError:
                raise Exception("Your cookie is missing the required value __Secure-3PAPISID")
            self._send_request('guide', {})

    def _send_request(self, endpoint: str, body: Dict, additionalParams: str = "") -> Dict:
        body.update(self.context)
        if self.auth:
            origin = self.headers.get('origin', self.headers.get('x-origin'))
            self.headers["Authorization"] = get_authorization(self.sapisid + ' ' + origin)
        response = self._session.post(base_url + endpoint + params + additionalParams,
                                      json=body,
                                      headers=self.headers,
                                      proxies=self.proxies)
        response_text = json.loads(response.text)
        if response.status_code >= 400:
            message = "Server returned HTTP " + str(
                response.status_code) + ": " + response.reason + ".\n"
            error = response_text.get('error', {}).get('message')
            raise Exception(message + error)
        return response_text

    def _check_auth(self):
        if not self.auth:
            raise Exception("Please provide authentication before using this function")

    @classmethod
    def setup(cls, filepath: str = None, headers_raw: str = None) -> Dict:
        """
        Requests browser headers from the user via command line
        and returns a string that can be passed to YTMusic()

        :param filepath: Optional filepath to store headers to.
        :param headers_raw: Optional request headers copied from browser.
            Otherwise requested from terminal
        :return: configuration headers string
        """
        return setup(filepath, headers_raw)

    def __enter__(self):
        return self

    def __exit__(self, execType=None, execValue=None, trackback=None):
        pass
