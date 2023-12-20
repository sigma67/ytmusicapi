from typing import Optional, Any
import time
import os
import json

from .base import OAuthToken, Token, Credentials


class RefreshingToken(Token):

    @classmethod
    def from_file(cls, file_path: str, credentials: Credentials, sync=True):
        if os.path.isfile(file_path):
            with open(file_path) as json_file:
                file_pack = json.load(json_file)

        return cls(OAuthToken(**file_pack), credentials, file_path if sync else None)

    def __init__(self,
                 token: OAuthToken,
                 credentials: Credentials,
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
        self._local_cache = path
        self.store_token()

    @property
    def access_token(self):
        if self.token.is_expiring:
            fresh = self.credentials.refresh_token(self.token.refresh_token)
            self.token.update(fresh)
            self.store_token()

        return self.token.access_token

    def store_token(self):
        if self.local_cache:
            with open(self.local_cache, encoding="utf8", mode='w') as file:
                json.dump(self.token.as_dict(), file, indent=True)

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

    def as_dict(self):
        return self.token.as_dict()
