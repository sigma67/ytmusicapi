from ytmusicapi import YTMusic


def test_ytmusic_context():
    with YTMusic(requests_session=False) as yt:
        assert isinstance(yt, YTMusic)
