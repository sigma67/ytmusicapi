from ytmusicapi.exceptions import YTMusicServerError


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
        results = yt.search("europe", filter="podcasts")
        for result in results:
            if result["browseId"] is None:
                continue  # search can surface non-podcast results even with the podcasts filter
            podcast = yt.get_podcast(result["browseId"])
            assert len(podcast) > 0

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
        results = yt.search("europe", filter="episodes")
        episodes = []
        for result in results:
            try:
                episode = yt.get_episode(result["videoId"])
            except YTMusicServerError:
                continue  # search can surface episodes that are no longer available
            episodes.append(episode)

        assert episodes
        assert all(
            episode["description"] is None or len(episode["description"].text) > 0 for episode in episodes
        )

    def test_get_episodes_playlist(self, yt_brand):
        playlist = yt_brand.get_episodes_playlist()
        assert len(playlist["episodes"]) > 80
        assert playlist["description"]
        assert playlist["year"]
        assert playlist["author"]["id"] and playlist["author"]["name"]
