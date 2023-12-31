import webbrowser
from typing import Dict, Optional

import requests

from ytmusicapi.constants import (
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_CODE_URL,
    OAUTH_SCOPE,
    OAUTH_TOKEN_URL,
    OAUTH_USER_AGENT,
)

from .base import Credentials, OAuthToken
from .exceptions import BadOAuthClient, UnauthorizedOAuthClient
from .models import AuthCodeDict, BaseTokenDict, RefreshableTokenDict
from .refreshing import RefreshingToken


class OAuthCredentials(Credentials):
    """
    Class for handling OAuth credential retrieval and refreshing.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        session: Optional[requests.Session] = None,
        proxies: Optional[Dict] = None,
    ):
        """
        :param client_id: Optional. Set the GoogleAPI client_id used for auth flows.
            Requires client_secret also be provided if set.
        :param client_secret: Optional. Corresponding secret for provided client_id.
        :param session: Optional. Connection pooling with an active session.
        :param proxies: Optional. Modify the session with proxy parameters.
        """
        # id, secret should be None, None or str, str
        if not isinstance(client_id, type(client_secret)):
            raise KeyError(
                "OAuthCredential init failure. Provide both client_id and client_secret or neither."
            )

        # bind instance to OAuth client for auth flows
        self.client_id = client_id if client_id else OAUTH_CLIENT_ID
        self.client_secret = client_secret if client_secret else OAUTH_CLIENT_SECRET

        self._session = session if session else requests.Session()  # for auth requests
        if proxies:
            self._session.proxies.update(proxies)

    def get_code(self) -> AuthCodeDict:
        """Method for obtaining a new user auth code. First step of token creation."""
        code_response = self._send_request(OAUTH_CODE_URL, data={"scope": OAUTH_SCOPE})
        return code_response.json()

    def _send_request(self, url, data):
        """Method for sending post requests with required client_id and User-Agent modifications"""

        data.update({"client_id": self.client_id})
        response = self._session.post(url, data, headers={"User-Agent": OAUTH_USER_AGENT})
        if response.status_code == 401:
            data = response.json()
            issue = data.get("error")
            if issue == "unauthorized_client":
                raise UnauthorizedOAuthClient("Token refresh error. Most likely client/token mismatch.")

            elif issue == "invalid_client":
                raise BadOAuthClient(
                    "OAuth client failure. Most likely client_id and client_secret mismatch or "
                    "YouTubeData API is not enabled."
                )
            else:
                raise Exception(
                    f"OAuth request error. status_code: {response.status_code}, url: {url}, content: {data}"
                )
        return response

    def token_from_code(self, device_code: str) -> RefreshableTokenDict:
        """Method for verifying user auth code and conversion into a FullTokenDict."""
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "http://oauth.net/grant_type/device/1.0",
                "code": device_code,
            },
        )
        return response.json()

    def prompt_for_token(self, open_browser: bool = False, to_file: Optional[str] = None) -> RefreshingToken:
        """
        Method for CLI token creation via user inputs.

        :param open_browser: Optional. Open browser to OAuth consent url automatically. (Default = False).
        :param to_file: Optional. Path to store/sync json version of resulting token. (Default = None).
        """

        code = self.get_code()
        url = f"{code['verification_url']}?user_code={code['user_code']}"
        if open_browser:
            webbrowser.open(url)
        input(f"Go to {url}, finish the login flow and press Enter when done, Ctrl-C to abort")
        raw_token = self.token_from_code(code["device_code"])
        ref_token = RefreshingToken(OAuthToken(**raw_token), credentials=self)
        if to_file:
            ref_token.local_cache = to_file
        return ref_token

    def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        """
        Method for requesting a new access token for a given refresh_token.
        Token must have been created by the same OAuth client.

        :param refresh_token: Corresponding refresh_token for a matching access_token.
            Obtained via
        """
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        return response.json()
