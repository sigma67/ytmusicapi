"""custom exception classes for ytmusicapi2"""


class YTMusicError(Exception):
    """base error class

    shall only be raised if none of the subclasses below are fitting
    """


class YTMusicUserError(YTMusicError):
    """error caused by invalid usage of ytmusicapi2"""


class YTMusicServerError(YTMusicError):
    """error caused by the YouTube Music backend"""
