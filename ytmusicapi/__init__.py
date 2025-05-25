from importlib.metadata import PackageNotFoundError, version

from ytmusicapi2.auth.oauth.credentials import OAuthCredentials
from ytmusicapi2.models.content.enums import LikeStatus
from ytmusicapi2.setup import setup, setup_oauth
from ytmusicapi2.ytmusic import YTMusic

try:
    __version__ = version("ytmusicapi2")
except PackageNotFoundError:
    # package is not installed
    pass

__copyright__ = "Copyright 2024 sigma67"
__license__ = "MIT"
__title__ = "ytmusicapi2"
__all__ = ["LikeStatus", "OAuthCredentials", "YTMusic", "setup", "setup_oauth"]
