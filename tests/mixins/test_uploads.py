import os
import stat
import tempfile
import time
from unittest import mock

import pytest

from tests.conftest import get_resource
from ytmusicapi.enums import ResponseStatus
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.ytmusic import YTMusic


class TestUploads:
    def test_get_library_upload_songs(self, yt_oauth, yt_empty):
        results = yt_oauth.get_library_upload_songs(50, order="z_to_a")
        assert len(results) > 25

        results = yt_empty.get_library_upload_songs(100)
        assert len(results) == 0

    def test_get_library_upload_albums(self, config, yt_oauth, yt_empty):
        results = yt_oauth.get_library_upload_albums(50, order="a_to_z")
        assert len(results) > 40

        albums = yt_oauth.get_library_upload_albums(None)
        assert len(albums) >= config.getint("limits", "library_upload_albums")

        results = yt_empty.get_library_upload_albums(100)
        assert len(results) == 0

    def test_get_library_upload_artists(self, config, yt_oauth, yt_empty):
        artists = yt_oauth.get_library_upload_artists(None)
        assert len(artists) >= config.getint("limits", "library_upload_artists")

        results = yt_oauth.get_library_upload_artists(50, order="recently_added")
        assert len(results) >= 25

        results = yt_empty.get_library_upload_artists(100)
        assert len(results) == 0

    def test_upload_song_exceptions(self, config, yt_auth, yt_oauth):
        with pytest.raises(Exception, match="The provided file does not exist."):
            yt_auth.upload_song("song.wav")
        with (
            tempfile.NamedTemporaryFile(suffix="wav") as temp,
            pytest.raises(Exception, match="The provided file type is not supported"),
        ):
            yt_auth.upload_song(temp.name)
        with pytest.raises(Exception, match="Please provide browser authentication"):
            yt_oauth.upload_song(config["uploads"]["file"])

    def test_upload_song(self, config, yt_auth):
        response = yt_auth.upload_song(get_resource(config["uploads"]["file"]))
        assert response.status_code == 409

    def test_upload_song_file_too_large(self, config, yt_auth):
        orig_os_stat = os.stat

        def fake_stat(arg, **kwargs):
            faked = list(orig_os_stat(arg))
            faked[stat.ST_SIZE] = 4 * 10**9
            return os.stat_result(faked)

        with (
            mock.patch("os.stat", side_effect=fake_stat),
            pytest.raises(YTMusicUserError, match="larger than the limit of 300MB"),
        ):
            yt_auth.upload_song(get_resource(config["uploads"]["file"]))

    def test_upload_song_and_verify(self, config, yt_auth: YTMusic):
        """Upload a song and verify it can be retrieved after it finishes processing."""
        upload_response = yt_auth.upload_song(get_resource(config["uploads"]["file"]))
        if not isinstance(upload_response, str) and upload_response.status_code == 409:
            # Song is already in uploads. Delete it and re-upload
            songs = yt_auth.get_library_upload_songs(limit=None, order="recently_added")
            delete_response = None
            for song in songs:
                if song.get("title") in config["uploads"]["file"]:
                    delete_response = yt_auth.delete_upload_entity(song["entityId"])
            assert delete_response == ResponseStatus.SUCCEEDED
            # Need to wait for song to be fully deleted
            time.sleep(10)
            # Now re-upload
            upload_response = yt_auth.upload_song(get_resource(config["uploads"]["file"]))

        assert upload_response == ResponseStatus.SUCCEEDED or upload_response.status_code == 200, (
            f"Song failed to upload {upload_response}"
        )

        # Wait for upload to finish processing and verify it can be retrieved
        retries_remaining = 5
        while retries_remaining:
            time.sleep(5)
            songs = yt_auth.get_library_upload_songs(limit=None, order="recently_added")
            for song in songs:
                if song.get("title") in config["uploads"]["file"]:
                    # Uploaded song found
                    return
            retries_remaining -= 1

        raise AssertionError("Uploaded song was not found in library")

    @pytest.mark.skip(reason="Do not delete uploads")
    def test_delete_upload_entity(self, yt_oauth):
        results = yt_oauth.get_library_upload_songs()
        response = yt_oauth.delete_upload_entity(results[0]["entityId"])
        assert response == ResponseStatus.SUCCEEDED

    def test_get_library_upload_album(self, config, yt_oauth):
        album = yt_oauth.get_library_upload_album(config["uploads"]["private_album_id"])
        assert len(album["tracks"]) > 0

    def test_get_library_upload_artist(self, config, yt_oauth):
        tracks = yt_oauth.get_library_upload_artist(config["uploads"]["private_artist_id"], 100)
        assert len(tracks) > 0
