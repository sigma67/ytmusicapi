import pytest

from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicUserError


def test_ytmusic_context():
    with YTMusic(requests_session=False) as yt:
        assert isinstance(yt, YTMusic)


def test_ytmusic_auth_error():
    with pytest.raises(YTMusicUserError, match="Invalid auth"):
        YTMusic(auth="def")
