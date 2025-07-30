class TestExplore:
    def test_get_mood_playlists(self, yt):
        categories = yt.get_mood_categories()
        assert len(list(categories)) > 0
        cat = next(iter(categories))
        assert len(categories[cat]) > 0
        playlists = yt.get_mood_playlists(categories[cat][0]["params"])
        assert len(playlists) > 0
