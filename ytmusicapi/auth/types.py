"""enum representing types of authentication supported by this library"""

from enum import Enum, auto


class AuthType(int, Enum):
    """enum representing types of authentication supported by this library"""

    UNAUTHORIZED = auto()

    BROWSER = auto()

    #: YTM instance is using a non-default OAuth client (id & secret)
    OAUTH_CUSTOM_CLIENT = auto()

    #: allows fully formed OAuth headers to ignore browser auth refresh flow
    OAUTH_CUSTOM_FULL = auto()
