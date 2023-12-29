import webbrowser
from typing import Dict, Optional

import requests
from requests.structures import CaseInsensitiveDict

from .models import FullTokenDict, BaseTokenDict, CodeDict
from .base import OAuthToken, Credentials
from .refreshing import RefreshingToken
from .exceptions import BadOAuthClient, UnauthorizedOAuthClient

from ytmusicapi.constants import (OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_CODE_URL,
                                  OAUTH_SCOPE, OAUTH_TOKEN_URL, OAUTH_USER_AGENT)


def is_oauth(headers: CaseInsensitiveDict) -> bool:
    oauth_structure = {
        "access_token",
        "expires_at",
        "expires_in",
        "token_type",
        "refresh_token",
    }
    return all(key in headers for key in oauth_structure)


class OAuthCredentials(Credentials):

    def __init__(self,
                 client_id: Optional[str] = OAUTH_CLIENT_ID,
                 client_secret: Optional[str] = OAUTH_CLIENT_SECRET,
                 session: Optional[requests.Session] = None,
                 proxies: Optional[Dict] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self._session = session if session else requests.Session()
        if proxies:
            self._session.proxies.update(proxies)

    def get_code(self) -> CodeDict:
        code_response = self._send_request(OAUTH_CODE_URL, data={"scope": OAUTH_SCOPE})
        return code_response.json()

    def _send_request(self, url, data):
        data.update({"client_id": self.client_id})
        response = self._session.post(url, data, headers={"User-Agent": OAUTH_USER_AGENT})
        if response.status_code == 401:
            data = response.json()
            issue = data.get('error')
            if issue == 'unauthorized_client':
                raise UnauthorizedOAuthClient(
                    'Token refresh error. Most likely client/token mismatch.')

            elif issue == 'invalid_client':
                raise BadOAuthClient(
                    'OAuth client failure. Most likely client_id and client_secret mismatch or '
                    'YouTubeData API is not enabled.')
            else:
                raise Exception(
                    f'OAuth request error. status_code: {response.status_code}, url: {url}, content: {data}'
                )
        return response

    def token_from_code(self, device_code: str) -> FullTokenDict:
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "http://oauth.net/grant_type/device/1.0",
                "code": device_code,
            },
        )
        return response.json()

    def prompt_for_token(self,
                         open_browser: bool = False,
                         to_file: Optional[str] = None) -> RefreshingToken:
        code = self.get_code()
        url = f"{code['verification_url']}?user_code={code['user_code']}"
        if open_browser:
            webbrowser.open(url)
        input(f"Go to {url}, finish the login flow and press Enter when done, Ctrl-C to abort")
        raw_token = self.token_from_code(code["device_code"])
        base_token = OAuthToken(**raw_token)
        ref_token = RefreshingToken(base_token, credentials=self)
        if to_file:
            ref_token.local_cache = to_file
        return ref_token

    def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        return response.json()
