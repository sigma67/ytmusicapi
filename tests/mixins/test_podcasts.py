class TestPodcasts:
    def test_get_channel(self, config, yt):
        podcast_id = config["podcasts"]["channel_id"]
        channel = yt.get_channel(podcast_id)
        assert len(channel["episodes"]["results"]) == 10
        assert len(channel["podcasts"]["results"]) >= 5

    def test_get_channel_episodes(self, config, yt_oauth):
        channel_id = config["podcasts"]["channel_id"]
        channel = yt_oauth.get_channel(channel_id)
        channel_episodes = yt_oauth.get_channel_episodes(channel_id, channel["episodes"]["params"])
        assert len(channel_episodes) >= 150
        assert len(channel_episodes[0]) == 9

    def test_get_podcast(self, config, yt, yt_brand):
        podcast_id = config["podcasts"]["podcast_id"]
        podcast = yt.get_podcast(podcast_id)
        assert len(podcast["episodes"]) == 100
        assert not podcast["saved"]
        assert podcast["thumbnails"]

        podcast = yt_brand.get_podcast(podcast_id, limit=None)
        assert len(podcast["episodes"]) > 100
        assert podcast["saved"]

    def test_many_podcasts(self, yt):
        results = yt.search("podcast", filter="podcasts")
        for result in results:
            results = yt.get_podcast(result["browseId"])
            assert len(results) > 0

    def test_get_episode(self, config, yt, yt_brand):
        episode_id = config["podcasts"]["episode_id"]
        episode = yt.get_episode(episode_id)
        assert len(episode["description"]) >= 20
        assert not episode["saved"]
        assert episode["playlistId"] is not None
        assert episode["thumbnails"]

        episode = yt_brand.get_episode(episode_id)
        assert episode["saved"]

    def test_many_episodes(self, yt):
        results = yt.search("episode", filter="episodes")
        for result in results:
            result = yt.get_episode(result["videoId"])
            assert len(result["description"].text) > 0

    def test_get_episodes_playlist(self, yt_brand):
        playlist = yt_brand.get_episodes_playlist()
        assert len(playlist["episodes"]) > 90
