"""models for oauth authentication"""

from typing import Literal, TypedDict

DefaultScope = str | Literal["https://www.googleapis.com/auth/youtube"]
Bearer = str | Literal["Bearer"]


class BaseTokenDict(TypedDict, total=False):
    """Limited token. Does not provide a refresh token. Commonly obtained via a token refresh."""

    access_token: str  #: str to be used in Authorization header
    expires_in: int  #: seconds until expiration from request timestamp
    scope: DefaultScope  #: should be 'https://www.googleapis.com/auth/youtube'
    token_type: Bearer  #: should be 'Bearer'


class RefreshableTokenDict(BaseTokenDict, total=False):
    """Entire token. Including refresh. Obtained through token setup."""

    expires_at: int  #: UNIX epoch timestamp in seconds
    refresh_token: str  #: str used to obtain new access token upon expiration


class AuthCodeDict(TypedDict, total=False):
    """Keys for the json object obtained via code response during auth flow."""

    device_code: str  #: code obtained via user confirmation and oauth consent
    user_code: str  #: alphanumeric code user is prompted to enter as confirmation. formatted as XXX-XXX-XXX.
    expires_in: int  #: seconds from original request timestamp
    interval: int  #: (?) "5" (?)
    verification_url: str  #: base url for OAuth consent screen for user signin/confirmation
