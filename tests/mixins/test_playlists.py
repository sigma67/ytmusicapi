import json
import time
from pathlib import Path
from unittest import mock

import pytest

from ytmusicapi import YTMusic
from ytmusicapi.constants import SUPPORTED_LANGUAGES
from ytmusicapi.enums import ResponseStatus
from ytmusicapi.exceptions import YTMusicUserError


class TestPlaylists:
    @pytest.mark.parametrize(
        "test_file, playlist_id",
        [
            ("2024_03_get_playlist.json", "PLaZPMsuQNCsWn0iVMtGbaUXO6z-EdZaZm"),
            ("2024_03_get_playlist_public.json", "RDCLAK5uy_lWy02cQBnTVTlwuRauaGKeUDH3L6PXNxI"),
            ("2024_07_get_playlist_collaborative.json", "PLEUijtLfpCOgI8LNOwiwvq0EJ8HAGj7dT"),
            ("2024_12_get_playlist_audio.json", "OLAK5uy_n0x1TMX8DL2eli2g_LysCSg-6Nq5YQa1g"),
        ],
    )
    def test_get_playlist(self, yt, test_file, playlist_id):
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / test_file, encoding="utf8") as f:
            mock_response = json.load(f)
        with open(data_dir / "expected_output" / test_file, encoding="utf8") as f:
            expected_output = json.load(f)

        with mock.patch("ytmusicapi.YTMusic._send_request", return_value=mock_response):
            playlist = yt.get_playlist(playlist_id)
            assert playlist_id == playlist["id"]

            assert playlist == playlist | expected_output

            for thumbnail in playlist.get("thumbnails", []):
                assert thumbnail["url"] and thumbnail["width"] and thumbnail["height"]

            assert len(playlist["tracks"]) > 0
            for track in playlist["tracks"]:
                assert isinstance(track["title"], str) and track["title"]

                assert len(track["artists"]) > 0
                for artist in track["artists"]:
                    assert isinstance(artist["name"], str) and artist["name"]

                if track["videoType"] == "MUSIC_VIDEO_TYPE_ATV":
                    assert isinstance(track["album"]["name"], str) and track["album"]["name"]

    @pytest.mark.parametrize(
        "playlist_id, tracks_len, related_len",
        [
            ("RDCLAK5uy_nfjzC9YC1NVPPZHvdoAtKVBOILMDOuxOs", 200, 10),
            ("PLj4BSJLnVpNyIjbCWXWNAmybc97FXLlTk", 200, 0),  # no related tracks
            ("PL6bPxvf5dW5clc3y9wAoslzqUrmkZ5c-u", 1000, 10),  # very large
            ("PL5ZNf-B8WWSZFIvpJWRjgt7iRqWT7_KF1", 10, 10),  # track duration > 1k hours
        ],
    )
    def test_get_playlist_foreign(self, yt_oauth, playlist_id, tracks_len, related_len):
        playlist = yt_oauth.get_playlist(playlist_id, limit=None, related=True)
        assert len(playlist["duration"]) > 5
        assert playlist["trackCount"] > tracks_len
        # serialize each track to detect duplicates
        assert len(set(json.dumps(track) for track in playlist["tracks"])) > tracks_len
        assert len(playlist["related"]) == related_len
        assert "suggestions" not in playlist
        assert playlist["owned"] is False

    def test_get_large_audio_playlist(self, yt_oauth):
        album = yt_oauth.get_playlist("OLAK5uy_noLNRtYnrcRVVO9rOyGMx64XyjVSCz1YU", limit=500)
        assert len(album["tracks"]) == 456

    def test_get_playlist_empty(self, yt_empty):
        with pytest.raises(Exception):
            yt_empty.get_playlist("PLABC")

    def test_get_playlist_no_track_count(self, yt_oauth):
        playlist = yt_oauth.get_playlist("RDATgXd-")
        assert playlist["trackCount"] is None  # playlist has no trackCount
        assert len(playlist["tracks"]) >= 100

    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_get_playlist_languages(self, language):
        yt = YTMusic(language=language)
        result = yt.get_playlist("PLj4BSJLnVpNyIjbCWXWNAmybc97FXLlTk")
        assert result["trackCount"] == 255

    def test_get_playlist_owned(self, config, yt_brand):
        playlist = yt_brand.get_playlist(config["playlists"]["own"], related=True, suggestions_limit=21)
        assert len(playlist["tracks"]) < 100
        assert len(playlist["suggestions"]) == 21
        assert len(playlist["related"]) == 10
        assert playlist["owned"] is True

    def test_edit_playlist(self, config, yt_brand):
        playlist = yt_brand.get_playlist(config["playlists"]["own"])
        response1 = yt_brand.edit_playlist(
            playlist["id"],
            title="",
            description="",
            privacyStatus="PRIVATE",
            moveItem=(
                playlist["tracks"][1]["setVideoId"],
                playlist["tracks"][0]["setVideoId"],
            ),
        )
        assert response1 == ResponseStatus.SUCCEEDED, "Playlist edit 1 failed"
        response2 = yt_brand.edit_playlist(
            playlist["id"],
            title=playlist["title"],
            description=playlist["description"],
            privacyStatus=playlist["privacy"],
            moveItem=(
                playlist["tracks"][0]["setVideoId"],
                playlist["tracks"][1]["setVideoId"],
            ),
        )
        assert response2 == ResponseStatus.SUCCEEDED, "Playlist edit 2 failed"
        response3 = yt_brand.edit_playlist(
            playlist["id"],
            title=playlist["title"],
            description=playlist["description"],
            privacyStatus=playlist["privacy"],
            moveItem=playlist["tracks"][0]["setVideoId"],
        )
        assert response3 == "STATUS_SUCCEEDED", "Playlist edit 3 failed"

    def test_create_playlist_invalid_title(self, yt_brand):
        with pytest.raises(YTMusicUserError, match="invalid characters"):
            yt_brand.create_playlist("test >", description="test")

    def test_end2end(self, yt_brand, sample_video):
        playlist_id = yt_brand.create_playlist(
            "test",
            "test description",
            source_playlist="OLAK5uy_lGQfnMNGvYCRdDq9ZLzJV2BJL2aHQsz9Y",
        )
        assert len(playlist_id) == 34, "Playlist creation failed"
        yt_brand.edit_playlist(playlist_id, addToTop=True)
        response = yt_brand.add_playlist_items(
            playlist_id,
            [sample_video, sample_video],
            source_playlist="OLAK5uy_nvjTE32aFYdFN7HCyMv3cGqD3wqBb4Jow",
            duplicates=True,
        )
        assert response["status"] == ResponseStatus.SUCCEEDED, "Adding playlist item failed"
        assert len(response["playlistEditResults"]) > 0, "Adding playlist item failed"
        time.sleep(3)
        yt_brand.edit_playlist(playlist_id, addToTop=False)
        time.sleep(3)
        playlist = yt_brand.get_playlist(playlist_id, related=True)
        assert len(playlist["tracks"]) == 46, "Getting playlist items failed"
        response = yt_brand.remove_playlist_items(playlist_id, playlist["tracks"])
        assert response == ResponseStatus.SUCCEEDED, "Playlist item removal failed"
        yt_brand.delete_playlist(playlist_id)
