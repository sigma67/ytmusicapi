from importlib.metadata import PackageNotFoundError, version

from ytmusicapi.setup import setup, setup_oauth
from ytmusicapi.ytmusic import YTMusic

try:
    __version__ = version("ytmusicapi")
except PackageNotFoundError:
    # package is not installed
    pass

__copyright__ = "Copyright 2023 sigma67"
__license__ = "MIT"
__title__ = "ytmusicapi"
__all__ = ["YTMusic", "setup_oauth", "setup"]
