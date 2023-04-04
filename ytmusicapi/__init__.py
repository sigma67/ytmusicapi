from ytmusicapi.ytmusic import YTMusic
from ytmusicapi.setup import setup, setup_oauth
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ytmusicapi")
except PackageNotFoundError:
    # package is not installed
    pass

__copyright__ = 'Copyright 2022 sigma67'
__license__ = 'MIT'
__title__ = 'ytmusicapi'
__all__ = ["YTMusic", "setup_oauth", "setup"]
