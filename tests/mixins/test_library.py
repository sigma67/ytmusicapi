from urllib.parse import urlparse

import pytest

from ytmusicapi.exceptions import YTMusicUserError


class TestLibrary:
    def test_get_library_playlists(self, config, yt_oauth, yt_empty):
        playlists = yt_oauth.get_library_playlists(50)
        assert len(playlists) > 25

        playlists = yt_oauth.get_library_playlists(None)
        assert len(playlists) >= config.getint("limits", "library_playlists")

        playlists = yt_empty.get_library_playlists()
        assert len(playlists) <= 1  # "Episodes saved for later"

    def test_get_library_songs(self, config, yt_oauth, yt_empty):
        with pytest.raises(Exception):
            yt_oauth.get_library_songs(None, True)
        songs = yt_oauth.get_library_songs(100)
        assert len(songs) >= 100
        songs = yt_oauth.get_library_songs(200, validate_responses=True)
        assert len(songs) >= config.getint("limits", "library_songs")
        songs = yt_oauth.get_library_songs(order="a_to_z")
        assert len(songs) >= 25
        songs = yt_empty.get_library_songs()
        assert len(songs) == 0

    def test_get_library_albums_invalid_order(self, yt):
        with pytest.raises(Exception):
            yt.get_library_albums(100, order="invalid")

    def test_get_library_albums(self, yt_oauth, yt_brand, yt_empty):
        albums = yt_oauth.get_library_albums(100)
        assert len(albums) > 50
        for album in albums:
            assert "playlistId" in album
        albums = yt_brand.get_library_albums(100, order="a_to_z")
        assert len(albums) > 50
        albums = yt_brand.get_library_albums(100, order="z_to_a")
        assert len(albums) > 50
        albums = yt_brand.get_library_albums(100, order="recently_added")
        assert len(albums) > 50
        albums = yt_empty.get_library_albums()
        assert len(albums) == 0

    def test_get_library_artists(self, config, yt_auth, yt_oauth, yt_brand, yt_empty):
        artists = yt_auth.get_library_artists(50)
        assert len(artists) > 40
        artists = yt_oauth.get_library_artists(order="a_to_z", limit=50)
        assert len(artists) > 40
        artists = yt_brand.get_library_artists(limit=None)
        assert len(artists) > config.getint("limits", "library_artists")
        artists = yt_empty.get_library_artists()
        assert len(artists) == 0

    def test_get_library_subscriptions(self, config, yt_brand, yt_empty):
        artists = yt_brand.get_library_subscriptions(50)
        assert len(artists) > 40
        artists = yt_brand.get_library_subscriptions(order="z_to_a")
        assert len(artists) > 20
        artists = yt_brand.get_library_subscriptions(limit=None)
        assert len(artists) > config.getint("limits", "library_subscriptions")
        artists = yt_empty.get_library_subscriptions()
        assert len(artists) == 0

    def test_get_library_podcasts(self, yt_brand, yt_empty):
        podcasts = yt_brand.get_library_podcasts(limit=50, order="a_to_z")
        assert len(podcasts) > 25

        empty = yt_empty.get_library_podcasts()
        assert len(empty) == 1  # saved episodes playlist is always there

    def test_get_library_channels(self, yt_brand, yt_empty):
        channels = yt_brand.get_library_channels(limit=50, order="recently_added")
        assert len(channels) > 25

        empty = yt_empty.get_library_channels()
        assert len(empty) == 0

    def test_get_liked_songs(self, yt_brand, yt_empty):
        songs = yt_brand.get_liked_songs(200)
        assert len(songs["tracks"]) > 100
        songs = yt_empty.get_liked_songs()
        assert songs["trackCount"] == 0

    def test_get_saved_episodes(self, yt_brand, yt_empty):
        episodes = yt_brand.get_saved_episodes(200)
        assert len(episodes["tracks"]) > 0
        episodes = yt_empty.get_saved_episodes()
        assert episodes["trackCount"] == 0

    def test_get_history(self, yt_oauth):
        songs = yt_oauth.get_history()
        assert len(songs) > 0
        assert all(song["feedbackToken"] is not None for song in songs)

    def test_manipulate_history_items(self, yt_auth, sample_video):
        song = yt_auth.get_song(sample_video)
        response = yt_auth.add_history_item(song)
        assert response.status_code == 204
        songs = yt_auth.get_history()
        assert len(songs) > 0
        response = yt_auth.remove_history_items([songs[0]["feedbackToken"]])
        assert "feedbackResponses" in response

    def test_rate_song(self, yt_auth, sample_video):
        response = yt_auth.rate_song(sample_video, "LIKE")
        assert "actions" in response
        response = yt_auth.rate_song(sample_video, "DISLIKE")
        assert "actions" in response
        response = yt_auth.rate_song(sample_video, "INDIFFERENT")
        assert response
        with pytest.raises(YTMusicUserError):
            yt_auth.rate_song(sample_video, "notexist")

    @pytest.mark.skip(reason="edit_song_library_status is currently broken due to server-side update")
    def test_edit_song_library_status(self, yt_brand, sample_album):
        album = yt_brand.get_album(sample_album)
        response = yt_brand.rate_playlist(album["tracks"][0]["feedbackTokens"]["add"])
        album = yt_brand.get_album(sample_album)
        assert album["tracks"][0]["inLibrary"]
        assert response["feedbackResponses"][0]["isProcessed"]
        response = yt_brand.edit_song_library_status(album["tracks"][0]["feedbackTokens"]["remove"])
        album = yt_brand.get_album(sample_album)
        assert not album["tracks"][0]["inLibrary"]
        assert response["feedbackResponses"][0]["isProcessed"]

    def test_rate_playlist(self, yt_auth):
        response = yt_auth.rate_playlist("OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4", "LIKE")
        assert "actions" in response
        response = yt_auth.rate_playlist("OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4", "INDIFFERENT")
        assert "actions" in response

    def test_subscribe_artists(self, yt_auth):
        yt_auth.subscribe_artists(["UCUDVBtnOQi4c7E8jebpjc9Q"])
        yt_auth.unsubscribe_artists(["UCUDVBtnOQi4c7E8jebpjc9Q"])

    def test_get_account_info(self, config, yt, yt_oauth):
        with pytest.raises(Exception, match="Please provide authentication"):
            yt.get_account_info()

        account_info = yt_oauth.get_account_info()
        assert account_info["accountName"] == config.get("auth", "account_name")
        assert account_info["channelHandle"] == config.get("auth", "channel_handle")
        assert bool(urlparse(account_info["accountPhotoUrl"]))
