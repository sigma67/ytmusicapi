import json
import time
import webbrowser
from typing import Dict, Optional, Any
from os import environ as env
import os

import requests
from requests.structures import CaseInsensitiveDict

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


class OAuthToken:

    @classmethod
    def from_response(cls, response):
        data = response.json()
        return cls(**data)

    def __init__(self,
                 access_token: str,
                 refresh_token: str,
                 scope: str,
                 token_type: str,
                 expires_at: Optional[int] = None,
                 expires_in: Optional[int] = None,
                 **etc: Optional[Any]):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._scope = scope
        self._expires_at: int = expires_at if expires_at else int(time.time() + expires_in)
        self._token_type = token_type

    @property
    def access_token(self):
        return self._access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def token_type(self):
        return self._token_type

    @property
    def scope(self):
        return self._scope

    @property
    def expires_at(self):
        return self._expires_at

    @property
    def expires_in(self):
        return self.expires_at - time.time()

    @property
    def is_expiring(self) -> bool:
        return self.expires_in < 60

    def as_dict(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'scope': self.scope,
            'expires_at': self.expires_at,
            'expires_in': self.expires_in,
            'token_type': self.token_type
        }

    def as_auth(self):
        return f'{self.token_type} {self.access_token}'


class OAuthCredentials:

    @classmethod
    def from_env(cls,
                 session: Optional[requests.Session] = None,
                 proxies: Optional[Dict] = None,
                 *,
                 client_id_key='YTMA_OAUTH_CLIENT_ID',
                 client_secret_key='YTMA_OAUTH_CLIENT_SECRET'):
        missing_keys = [x for x in [client_id_key, client_secret_key] if x not in env]
        if missing_keys:
            raise KeyError('Failed to build credentials from environment. Missing required keys: ',
                           missing_keys)

        return cls(client_id=env[client_id_key],
                   client_secret=env[client_secret_key],
                   session=session,
                   proxies=proxies)

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

    def get_code(self) -> Dict:
        code_response = self._send_request(OAUTH_CODE_URL, data={"scope": OAUTH_SCOPE})
        return code_response.json()

    def _send_request(self, url, data):
        data.update({"client_id": self.client_id})
        return self._session.post(url, data, headers={"User-Agent": OAUTH_USER_AGENT})

    def token_from_code(self, device_code: str) -> OAuthToken:
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "http://oauth.net/grant_type/device/1.0",
                "code": device_code,
            },
        )
        return OAuthToken.from_response(response)

    def prompt_for_token(self, open_browser: bool = False, to_file: Optional[str] = None):
        code = self.get_code()
        url = f"{code['verification_url']}?user_code={code['user_code']}"
        if open_browser:
            webbrowser.open(url)
        input(f"Go to {url}, finish the login flow and press Enter when done, Ctrl-C to abort")
        raw_token = self.token_from_code(code["device_code"])
        ref_token = RefreshingToken(raw_token, credentials=self)
        if to_file:
            ref_token.local_cache = to_file
        return ref_token

    def refresh_token(self, refresh_token: str) -> OAuthToken:
        response = self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        return OAuthToken.from_response(response)


class RefreshingToken(OAuthToken):

    @classmethod
    def from_file(cls, file_path: str, credentials: Optional[OAuthCredentials] = None, sync=True):
        if os.path.isfile(file_path):
            with open(file_path) as json_file:
                file_pack = json.load(json_file)

        creds = credentials if credentials else OAuthCredentials()

        return cls(OAuthToken(**file_pack), creds, file_path if sync else None)

    def __init__(self,
                 token: OAuthToken,
                 credentials: OAuthCredentials,
                 local_cache: Optional[str] = None):
        self.token = token
        self.credentials = credentials
        self._local_cache = local_cache

    @property
    def local_cache(self):
        return self._local_cache

    # as a property so swapping it will automatically dump the token to the new location
    @local_cache.setter
    def local_cache(self, path: str):
        with open(path, encoding="utf8", mode='w') as file:
            json.dump(self.token.as_dict(), file, indent=True)
        self._local_cache = path

    @property
    def access_token(self):
        if self.token.is_expiring:
            self.token = self.credentials.refresh_token(self.token.refresh_token)
            # update stored token file on refresh when provided
            if self.local_cache:
                with open(self.local_cache, encoding="utf8", mode='w') as file:
                    json.dump(self.token.as_dict(), file, indent=True)
        return self.token.access_token

    @property
    def refresh_token(self):
        return self.token.refresh_token

    @property
    def is_expiring(self) -> bool:
        return False

    @property
    def expires_at(self):
        return None

    @property
    def expires_in(self):
        return None

    @property
    def scope(self):
        return self.token.scope

    @property
    def token_type(self):
        return self.token.token_type
