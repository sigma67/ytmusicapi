"""custom exception classes for ytmusicapi"""


class YTMusicError(Exception):
    """base error class

    shall only be raised if none of the subclasses below are fitting
    """


class YTMusicUserError(YTMusicError):
    """error caused by invalid usage of ytmusicapi"""


class YTMusicServerError(YTMusicError):
    """error caused by the YouTube Music backend"""
