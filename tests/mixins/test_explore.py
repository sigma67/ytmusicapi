class TestExplore:
    def test_get_mood_playlists(self, yt):
        categories = yt.get_mood_categories()
        assert len(list(categories)) > 0
        cat = next(iter(categories))
        assert len(categories[cat]) > 0
        playlists = yt.get_mood_playlists(categories[cat][0]["params"])
        assert len(playlists) > 0

    def test_get_explore(self, yt, yt_oauth):
        assert len(yt.get_explore()) >= 4

        explore = yt_oauth.get_explore()
        assert len(explore) >= 5

        assert all(item["audioPlaylistId"].startswith("OLA") for item in explore["new_releases"])

        # check top_songs if present
        for item in explore.get("top_songs", {"items": []})["items"]:
            assert item["videoId"], item
            assert item["videoType"], item
            assert item.get("views") or item.get("album"), item

        for item in explore["trending"]["items"]:
            assert item["videoId"], item
            assert item["videoType"], item
            if podcast := item.get("podcast", None):
                assert podcast["id"], item
                assert podcast["name"], item

        assert any(artist["id"] for artist in item["artists"] for item in explore["trending"]["items"]), [
            artist["id"] for artist in item["artists"] for item in explore["trending"]["items"]
        ]

        if "top_episodes" in explore:
            for item in explore["top_episodes"]:
                assert item["videoId"], item
                assert item["videoType"], item
                assert item["duration"], item
                assert item["podcast"]["id"], item
                assert item["podcast"]["name"], item
