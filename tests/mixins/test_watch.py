import pytest


class TestWatch:
    def test_get_watch_playlist(self, config, yt, yt_brand, yt_oauth):
        playlist = yt_oauth.get_watch_playlist(
            playlistId="RDAMPLOLAK5uy_l_fKDQGOUsk8kbWsm9s86n4-nZNd2JR8Q",
            radio=True,
            limit=90,
        )
        assert len(playlist["tracks"]) >= 90
        playlist = yt_oauth.get_watch_playlist("9mWr4c_ig54", limit=50)
        assert len(playlist["tracks"]) > 45
        playlist = yt_oauth.get_watch_playlist("UoAf_y9Ok4k")  # private track
        assert len(playlist["tracks"]) >= 25
        playlist = yt.get_watch_playlist(playlistId=config["albums"]["album_browse_id"], shuffle=True)
        assert len(playlist["tracks"]) == config.getint("albums", "album_track_length")
        playlist = yt_brand.get_watch_playlist(playlistId=config["playlists"]["own"], shuffle=True)
        assert len(playlist["tracks"]) == config.getint("playlists", "own_length")

    def test_get_watch_playlist_errors(self, config, yt):
        with pytest.raises(Exception, match="No content returned by the server"):
            yt.get_watch_playlist(playlistId="PL_NOT_EXIST")
