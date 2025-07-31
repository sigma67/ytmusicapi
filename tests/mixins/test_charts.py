class TestCharts:
    def test_get_charts(self, yt, yt_oauth):
        charts = yt_oauth.get_charts()
        assert len(charts) >= 3
        charts = yt.get_charts(country="US")
        assert len(charts) == 4  # countries, videos, genres, artists
        charts = yt.get_charts(country="BE")
        assert len(charts) == 3  # countries, videos, artists
