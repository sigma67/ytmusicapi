from importlib.metadata import PackageNotFoundError, version

from ytmusicapi.setup import setup, setup_oauth
from ytmusicapi.ytmusic import YTMusic
from .mixins.browsing import Lyrics, TimedLyrics, LyricLine

try:
    __version__ = version("ytmusicapi")
except PackageNotFoundError:
    # package is not installed
    pass

__copyright__ = "Copyright 2024 sigma67"
__license__ = "MIT"
__title__ = "ytmusicapi"
__all__ = ["YTMusic", "setup_oauth", "setup",
           "Lyrics", "TimedLyrics", "LyricLine"]
