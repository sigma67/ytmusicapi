class TestExplore:
    def test_get_mood_playlists(self, yt):
        categories = yt.get_mood_categories()
        assert len(list(categories)) > 0
        cat = next(iter(categories))
        assert len(categories[cat]) > 0
        playlists = yt.get_mood_playlists(categories[cat][0]["params"])
        assert len(playlists) > 0

    def test_get_charts(self, yt, yt_oauth):
        charts = yt_oauth.get_charts()
        # songs section appears to be removed currently (US)
        assert len(charts) >= 3
        charts = yt.get_charts(country="US")
        assert len(charts) == 5
        charts = yt.get_charts(country="BE")
        assert len(charts) == 4
