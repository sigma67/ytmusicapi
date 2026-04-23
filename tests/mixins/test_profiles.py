from unittest.mock import patch

from ytmusicapi.enums import ProfileTypes


class TestProfiles:
    artist_id = "MPLAUCmMUZbaYdNH0bEd1PAlAqsA"
    artist_id_no_album_year = "UCLZ7tlKC06ResyDmEStSrOw"
    user_id = "UC44hbeRoCZVVMVg5z0FfIww"

    def test_get_artist(self, yt):
        results = yt.get_artist(self.artist_id)
        assert len(results) == 17
        assert results["shuffleId"] is not None
        assert results["radioId"] is not None

        # test correctness of related artists
        related = results["related"]["results"]
        assert len(
            [x for x in related if set(x.keys()) == {"browseId", "subscribers", "title", "thumbnails"}]
        ) == len(related)

    def test_get_artist__no_album_year(self, yt):
        results = yt.get_artist(self.artist_id_no_album_year)  # no album year
        assert len(results) >= 11

    def test_get_user(self, yt):
        results = yt.get_user(self.user_id)
        assert len(results) == 3

    def test_get_channel(self, config, yt):
        podcast_id = config["podcasts"]["channel_id"]
        channel = yt.get_channel(podcast_id)
        assert len(channel["episodes"]["results"]) == 10
        assert len(channel["podcasts"]["results"]) >= 5

    def test_determine_type__artist(self, yt):
        determined_type, _ = yt.get_profile(self.artist_id)
        assert determined_type == ProfileTypes.ARTIST

    def test_determine_type__user(self, yt):
        determined_type, _ = yt.get_profile(self.user_id)
        assert determined_type == ProfileTypes.USER

    def test_determine_type__channel(self, config, yt):
        determined_type, _ = yt.get_profile(config["podcasts"]["channel_id"])
        assert determined_type == ProfileTypes.CHANNEL

    def test_profile_type_not_ignored(self, yt):
        with (
            patch.object(yt, "_determine_profile_type") as determine_type_mock,
            patch.object(yt, "_send_request"),
            patch.object(yt, "_parse_artist") as parse_artist_mock,
        ):
            yt.get_profile(self.user_id, ProfileTypes.ARTIST)

        determine_type_mock.assert_not_called()
        parse_artist_mock.assert_called_once()
