from typing import Optional, Any, Union, Dict
import time
import json

from .models import BaseTokenDict, DefaultScope, Bearer, FullTokenDict


class Credentials:
    """ Base class representation of YouTubeMusicAPI OAuth Credentials """
    client_id: str
    client_secret: str

    def get_code(self) -> Dict:
        raise NotImplementedError()

    def token_from_code(self, device_code: str) -> FullTokenDict:
        raise NotImplementedError()

    def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        raise NotImplementedError()


class Token:
    """ Base class representation of the YouTubeMusicAPI OAuth token """
    access_token: str
    refresh_token: str
    expires_in: str
    expires_at: str

    scope: Union[str, DefaultScope]
    token_type: Union[str, Bearer]

    def as_dict(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'scope': self.scope,
            'expires_at': self.expires_at,
            'expires_in': self.expires_in,
            'token_type': self.token_type
        }

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_auth(self):
        return f'{self.token_type} {self.access_token}'


class OAuthToken(Token):

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

    def update(self, fresh_access: BaseTokenDict):
        self._access_token = fresh_access['access_token']
        self._expires_at = int(time.time() + fresh_access['expires_in'])

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
