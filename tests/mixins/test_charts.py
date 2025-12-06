class TestCharts:
    def test_get_charts(self, yt, yt_oauth):
        charts = yt_oauth.get_charts()
        assert len(charts) >= 3
        # authed sessions should have ranked artists
        assert all([artist["rank"] and artist["trend"] for artist in charts["artists"]])
        charts = yt.get_charts(country="US")
        assert len(charts) == 4  # countries, videos, genres, artists
        charts = yt.get_charts(country="BE")
        assert len(charts) == 3  # countries, videos, artists
