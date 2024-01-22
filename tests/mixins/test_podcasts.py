class TestPodcasts:
    def test_get_podcast(self, yt, yt_brand):
        podcast_id = "PLxq_lXOUlvQDgCVFj9L79kqJybW0k6OaB"  # Think Fast, Talk Smart: The Podcast

        results = yt.get_podcast(podcast_id)
        assert len(results["episodes"]) == 100
        assert not results["saved"]

        results = yt_brand.get_podcast(podcast_id, limit=None)
        assert len(results["episodes"]) > 100
        assert results["saved"]

    def test_many_podcasts(self, yt):
        results = yt.search("podcast", filter="podcasts")
        for result in results:
            results = yt.get_podcast(result["browseId"])
            assert len(results) > 0

    def test_get_episode(self, yt, yt_brand):
        podcast_id = "KNkyHCLOr1o"  # 124. Making Meetings Meaningful, Pt. 1: How to Structure
        result = yt.get_episode(podcast_id)
        assert len(result["description"]) == 50
        assert not result["saved"]
        assert result["playlistId"] is not None

        result = yt_brand.get_episode(podcast_id)
        assert result["saved"]

    def test_many_episodes(self, yt):
        results = yt.search("episode", filter="episodes")
        for result in results:
            result = yt.get_episode(result["videoId"])
            assert len(result["description"].text) > 0
