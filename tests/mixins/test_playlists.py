import json
import time
from pathlib import Path
from unittest import mock

import pytest

from ytmusicapi import YTMusic
from ytmusicapi.constants import SUPPORTED_LANGUAGES
from ytmusicapi.enums import ResponseStatus


class TestPlaylists:
    @pytest.mark.parametrize(
        ("test_file", "owned"),
        [
            ("2024_03_get_playlist.json", True),
            ("2024_03_get_playlist_public.json", False),
            ("2024_07_get_playlist_collaborative.json", True),
        ],
    )
    def test_get_playlist_2024(self, yt, test_file, owned):
        with open(Path(__file__).parent.parent / "data" / test_file, encoding="utf8") as f:
            mock_response = json.load(f)
        with mock.patch("ytmusicapi.YTMusic._send_request", return_value=mock_response):
            playlist = yt.get_playlist("MPREabc")
            assert playlist["year"] == "2024"
            assert playlist["owned"] == owned
            assert "hours" in playlist["duration"] or "minutes" in playlist["duration"]
            assert playlist["id"]
            assert isinstance(playlist["description"], str) and playlist["description"]
            assert len(playlist["tracks"]) > 0

            for track in playlist["tracks"]:
                assert isinstance(track["title"], str) and track["title"]

                assert len(track["artists"]) > 0
                for artist in track["artists"]:
                    assert isinstance(artist["name"], str) and artist["name"]

                if track["videoType"] == "MUSIC_VIDEO_TYPE_ATV":
                    assert isinstance(track["album"]["name"], str) and track["album"]["name"]

    def test_get_playlist_foreign(self, yt, yt_auth, yt_oauth):
        with pytest.raises(Exception):
            yt.get_playlist("PLABC")
        playlist = yt_auth.get_playlist("RDCLAK5uy_nfjzC9YC1NVPPZHvdoAtKVBOILMDOuxOs", limit=300, suggestions_limit=7)
        assert len(playlist["duration"]) > 5
        assert len(playlist["tracks"]) > 200
        assert "suggestions" not in playlist
        assert playlist["owned"] is False

        yt.get_playlist("RDATgXd-")
        assert len(playlist["tracks"]) >= 100

        playlist = yt_oauth.get_playlist("PLj4BSJLnVpNyIjbCWXWNAmybc97FXLlTk", limit=None, related=True)
        assert len(playlist["tracks"]) > 200
        assert len(playlist["related"]) == 0

        playlist = yt_oauth.get_playlist("PLAKw47hquUsKSPUT-NjU2B9HXYkdaCG8G", limit=None)
        assert len(playlist["tracks"]) > 1000
        assert len(playlist["related"]) == 0

    def test_get_playlist_foreign_new_format(self, yt_empty):
        with pytest.raises(Exception):
            yt_empty.get_playlist("PLABC")
        playlist = yt_empty.get_playlist("RDCLAK5uy_nfjzC9YC1NVPPZHvdoAtKVBOILMDOuxOs", limit=300, suggestions_limit=7)
        assert len(playlist["duration"]) > 5
        assert len(playlist["tracks"]) > 200
        assert "suggestions" not in playlist
        assert playlist["owned"] is False

        playlist = yt_empty.get_playlist("RDATgXd-")
        assert len(playlist["tracks"]) >= 100

        playlist = yt_empty.get_playlist("PLj4BSJLnVpNyIjbCWXWNAmybc97FXLlTk", limit=None, related=True)
        assert len(playlist["tracks"]) > 200
        assert len(playlist["related"]) == 0

        playlist = yt_empty.get_playlist("PLAKw47hquUsKSPUT-NjU2B9HXYkdaCG8G", limit=None)
        assert len(playlist["tracks"]) > 1000
        assert len(playlist["related"]) == 0

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
