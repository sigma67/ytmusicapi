from functools import partial

import pytest
import requests

from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicUserError


def test_ytmusic_context():
    with YTMusic(requests_session=False) as yt:
        assert isinstance(yt, YTMusic)


def test_ytmusic_auth_error():
    with pytest.raises(YTMusicUserError, match="Invalid auth"):
        YTMusic(auth="def")


def test_ytmusic_session():
    test_session = requests.Session()
    test_session.request = partial(test_session.request, timeout=60)
    ytmusic = YTMusic(requests_session=test_session)
    assert ytmusic._session == test_session

    ytmusic = YTMusic()
    assert isinstance(ytmusic._session, requests.Session)
    assert ytmusic._session != test_session
