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
        assert all(item["videoId"] for item in explore.get("top_songs", {"items": []})["items"])

        assert all(
            item["videoId"] and all(artist["id"] for artist in item["artists"])
            for item in explore["trending"]["items"]
        )

        assert all(item["videoId"] for item in explore["trending"]["items"])

        assert all(
            item["duration"] and item["podcast"]["id"] and item["podcast"]["name"]
            for item in explore["top_episodes"]
        )
