import json
import os
from typing import Optional

from .base import Credentials, OAuthToken, Token
from .models import Bearer, RefreshableTokenDict


class RefreshingToken(Token):
    """
    Compositional implementation of Token that automatically refreshes
    an underlying OAuthToken when required (credential expiration <= 1 min)
    upon access_token attribute access.
    """

    @classmethod
    def from_file(cls, file_path: str, credentials: Credentials, sync=True):
        """
        Initialize a refreshing token and underlying OAuthToken directly from a file.

        :param file_path: path to json containing token values
        :param credentials: credentials used with token in file.
        :param sync: Optional. Whether to pass the filepath into instance enabling file
            contents to be updated upon refresh. (Default=True).
        :return: RefreshingToken instance
        :rtype: RefreshingToken
        """

        if os.path.isfile(file_path):
            with open(file_path) as json_file:
                file_pack = json.load(json_file)

        return cls(OAuthToken(**file_pack), credentials, file_path if sync else None)

    def __init__(self, token: OAuthToken, credentials: Credentials, local_cache: Optional[str] = None):
        """
        :param token: Underlying Token being maintained.
        :param credentials: OAuth client being used for refreshing.
        :param local_cache: Optional. Path to json file where token values are stored.
            When provided, file contents is updated upon token refresh.
        """

        self.token: OAuthToken = token  #: internal token being used / refreshed / maintained
        self.credentials = credentials  #: credentials used for access_token refreshing

        #: protected/property attribute enables auto writing token
        #  values to new file location via setter
        self._local_cache = local_cache

    @property
    def token_type(self) -> Bearer:
        return self.token.token_type

    @property
    def local_cache(self) -> str | None:
        return self._local_cache

    @local_cache.setter
    def local_cache(self, path: str):
        """Update attribute and dump token to new path."""
        self._local_cache = path
        self.store_token()

    @property
    def access_token(self) -> str:
        if self.token.is_expiring:
            fresh = self.credentials.refresh_token(self.token.refresh_token)
            self.token.update(fresh)
            self.store_token()

        return self.token.access_token

    def store_token(self, path: Optional[str] = None) -> None:
        """
        Write token values to json file at specified path, defaulting to self.local_cache.
        Operation does not update instance local_cache attribute.
        Automatically called when local_cache is set post init.
        """
        file_path = path if path else self.local_cache

        if file_path:
            with open(file_path, encoding="utf8", mode="w") as file:
                json.dump(self.token.as_dict(), file, indent=True)

    def as_dict(self) -> RefreshableTokenDict:
        # override base class method with call to underlying token's method
        return self.token.as_dict()
