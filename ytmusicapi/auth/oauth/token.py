import json
import time
import webbrowser
from collections.abc import KeysView
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.oauth.credentials import Credentials, OAuthCredentials
from ytmusicapi.auth.oauth.models import BaseTokenDict, Bearer, DefaultScope, RefreshableTokenDict


@dataclass(kw_only=True)
class Token:
    """Base class representation of the YouTubeMusicAPI OAuth token."""

    scope: DefaultScope
    token_type: Bearer

    access_token: str
    refresh_token: str
    expires_at: int = 0
    expires_in: int = 0

    @staticmethod
    def members() -> KeysView[str]:
        return Token.__annotations__.keys()

    def __repr__(self) -> str:
        """Readable version."""
        return f"{self.__class__.__name__}: {self.as_dict()}"

    def as_dict(self) -> RefreshableTokenDict:
        """Returns dictionary containing underlying token values."""
        return {key: self.__dict__[key] for key in Token.members()}  # type: ignore

    def as_json(self) -> str:
        return json.dumps(self.as_dict())

    def as_auth(self) -> str:
        """Returns Authorization header ready str of token_type and access_token."""
        return f"{self.token_type} {self.access_token}"

    @property
    def is_expiring(self) -> bool:
        return self.expires_in < 60


class OAuthToken(Token):
    """Wrapper for an OAuth token implementing expiration methods."""

    @staticmethod
    def is_oauth(headers: CaseInsensitiveDict[str]) -> bool:
        return all(key in headers for key in Token.members())

    def update(self, fresh_access: BaseTokenDict) -> None:
        """
        Update access_token and expiration attributes with a BaseTokenDict inplace.
        expires_at attribute set using current epoch, avoid expiration desync
        by passing only recently requested tokens dicts or updating values to compensate.
        """
        self.access_token = fresh_access["access_token"]
        self.expires_at = int(time.time()) + fresh_access["expires_in"]

    @property
    def is_expiring(self) -> bool:
        return self.expires_at - int(time.time()) < 60

    @classmethod
    def from_json(cls, file_path: Path) -> "OAuthToken":
        if file_path.is_file():
            with open(file_path) as json_file:
                file_pack = json.load(json_file)

        return cls(**file_pack)


@dataclass
class RefreshingToken(OAuthToken):
    """
    Compositional implementation of Token that automatically refreshes
    an underlying OAuthToken when required (credential expiration <= 1 min)
    upon access_token attribute access.
    """

    #: credentials used for access_token refreshing
    credentials: Credentials

    #: protected/property attribute enables auto writing token values to new file location via setter
    _local_cache: Path | None = None

    def __getattribute__(self, item: str) -> Any:
        """access token setter to auto-refresh if it is expiring"""
        if item == "access_token" and self.is_expiring:
            fresh = self.credentials.refresh_token(self.refresh_token)
            self.update(fresh)
            self.store_token()

        return super().__getattribute__(item)

    @property
    def local_cache(self) -> Path | None:
        return self._local_cache

    @local_cache.setter
    def local_cache(self, path: Path) -> None:
        """Update attribute and dump token to new path."""
        self._local_cache = path
        self.store_token()

    @classmethod
    def prompt_for_token(
        cls, credentials: OAuthCredentials, open_browser: bool = False, to_file: str | None = None
    ) -> "RefreshingToken":
        """
        Method for CLI token creation via user inputs.

        :param credentials: Client credentials
        :param open_browser: Optional. Open browser to OAuth consent url automatically. (Default: ``False``).
        :param to_file: Optional. Path to store/sync json version of resulting token. (Default: ``None``).
        """

        code = credentials.get_code()
        url = f"{code['verification_url']}?user_code={code['user_code']}"
        if open_browser:
            webbrowser.open(url)
        input(f"Go to {url}, finish the login flow and press Enter when done, Ctrl-C to abort")
        raw_token = credentials.token_from_code(code["device_code"])
        ref_token = cls(credentials=credentials, **raw_token)
        ref_token.update(ref_token.as_dict())
        if to_file:
            ref_token.local_cache = Path(to_file)
        return ref_token

    def store_token(self, path: str | None = None) -> None:
        """
        Write token values to json file at specified path, defaulting to self.local_cache.
        Operation does not update instance local_cache attribute.
        Automatically called when local_cache is set post init.
        """
        file_path = path if path else self.local_cache

        if file_path:
            with open(file_path, encoding="utf8", mode="w") as file:
                json.dump(self.as_dict(), file, indent=True)
