# stand-in classes for clarity until pydantic implementation

from typing import Union, Literal, TypedDict

DefaultScope = Literal['https://www.googleapis.com/auth/youtube']
Bearer = Literal['Bearer']


class BaseTokenDict(TypedDict):
    """ Limited token. Does not provide a refresh token. Commonly obtained via a token refresh. """
    access_token: str
    expires_in: int
    scope: Union[str, DefaultScope]
    token_type: Union[str, Bearer]


class FullTokenDict(BaseTokenDict):
    """ Entire token. Including refresh. Obtained through token setup. """
    expires_at: int
    refresh_token: str


class CodeDict(TypedDict):
    """ Keys for the json object obtained via code response during auth flow. """
    device_code: str
    user_code: str
    expires_in: int
    interval: int
    verification_url: str
