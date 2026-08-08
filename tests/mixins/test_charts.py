import json
from unittest import mock


class TestCharts:
    def test_get_charts(self, yt, yt_oauth):
        charts = yt_oauth.get_charts()
        assert len(charts) >= 3
        # authed sessions should have ranked artists
        assert all(artist["rank"] and artist["trend"] for artist in charts["artists"])
        charts = yt.get_charts(country="US")
        assert {"countries", "videos", "artists"} <= charts.keys()  # "genres" is not always returned
        charts = yt.get_charts(country="BE")
        assert charts.keys() == {"countries", "videos", "artists"}

    def test_get_charts_us_carousels(self, yt, data_path):
        """some US responses omit the genres carousel and add an album one, neither of which
        may shift the known categories"""
        with open(data_path / "2026_07_get_charts_us_albums_no_genres.json", encoding="utf8") as f:
            mock_response = json.load(f)

        with mock.patch("ytmusicapi.YTMusic._send_request", return_value=mock_response):
            charts = yt.get_charts(country="US")

        assert charts.keys() == {"countries", "videos", "artists"}
        assert len(charts["videos"]) > 0
        assert len(charts["artists"]) > 0
