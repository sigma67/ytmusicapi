import json
from pathlib import Path
from unittest import mock


class TestExplore:
    def test_get_mood_playlists(self, yt):
        categories = yt.get_mood_categories()
        assert len(list(categories)) > 0
        cat = next(iter(categories))
        assert len(categories[cat]) > 0
        playlists = yt.get_mood_playlists(categories[cat][0]["params"])
        assert len(playlists) > 0

    def test_get_explore(self, yt, yt_oauth):
        assert len(yt.get_explore()) == 5

        explore = yt_oauth.get_explore()
        assert len(explore) >= 5

        assert all(item["audioPlaylistId"].startswith("OLA") for item in explore["new_releases"])

        # check top_songs if present
        assert all(
            item["videoId"] and item["videoType"] and (item.get("views") or item.get("album"))
            for item in explore.get("top_songs", {"items": []})["items"]
        )

        assert all(
            item["videoId"]
            and item["videoType"]
            and (
                podcast["id"] and podcast["name"]
                if (podcast := item.get("podcast", None))
                else all(artist["id"] for artist in item["artists"])
            )
            for item in explore["trending"]["items"]
        )

        assert all(
            item["videoId"]
            and item["videoType"]
            and item["duration"]
            and item["podcast"]["id"]
            and item["podcast"]["name"]
            for item in explore["top_episodes"]
        )

    def test_get_explore_2025(self, yt):
        data_dir = Path(__file__).parent.parent / "data"
        test_file = "2025_11_get_explore.json"
        with open(data_dir / test_file, encoding="utf8") as f:
            mock_response = json.load(f)
        with mock.patch("ytmusicapi.YTMusic._send_request", return_value=mock_response):
            result = yt.get_explore()
        with open(data_dir / "expected_output" / test_file, encoding="utf8") as f:
            expected_output = json.load(f)
        assert result == expected_output
