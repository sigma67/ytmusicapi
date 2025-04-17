import json
import warnings
from pathlib import Path
from unittest import mock

import pytest

from tests.test_helpers import is_ci
from ytmusicapi.models.lyrics import LyricLine


class TestBrowsing:
    def test_get_home(self, yt, yt_auth):
        result = yt.get_home()
        assert len(result) >= 2
        result = yt_auth.get_home(limit=15)
        assert len(result) >= 15

    def test_get_artist(self, yt):
        results = yt.get_artist("MPLAUCmMUZbaYdNH0bEd1PAlAqsA")
        assert len(results) == 16
        assert results["shuffleId"] is not None
        assert results["radioId"] is not None

        # test correctness of related artists
        related = results["related"]["results"]
        assert len(
            [x for x in related if set(x.keys()) == {"browseId", "subscribers", "title", "thumbnails"}]
        ) == len(related)

        results = yt.get_artist("UCLZ7tlKC06ResyDmEStSrOw")  # no album year
        assert len(results) >= 11

    def test_get_artist_shows(self, yt_oauth):
        # with audiobooks - only with authentication
        results = yt_oauth.get_artist("UCyiY-0Af0O6emoI3YvCEDaA")
        assert len(results["shows"]["results"]) == 10

        results = yt_oauth.get_artist_albums(results["shows"]["browseId"], results["shows"]["params"])
        assert len(results) == 100

    def test_get_artist_albums(self, yt):
        artist = yt.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = yt.get_artist_albums(artist["albums"]["browseId"], artist["albums"]["params"])
        assert len(results) == 100
        results = yt.get_artist_albums(artist["singles"]["browseId"], artist["singles"]["params"])
        assert len(results) == 100

        results_unsorted = yt.get_artist_albums(
            artist["albums"]["browseId"], artist["albums"]["params"], limit=None
        )
        assert len(results_unsorted) >= 300

        results_sorted = yt.get_artist_albums(
            artist["albums"]["browseId"], artist["albums"]["params"], limit=None, order="alphabetical order"
        )
        assert len(results_sorted) >= 300
        assert results_sorted != results_unsorted

        with pytest.raises(ValueError, match="Invalid order"):
            yt.get_artist_albums(artist["albums"]["browseId"], artist["albums"]["params"], order="order")

    def test_get_user(self, yt):
        results = yt.get_user("UC44hbeRoCZVVMVg5z0FfIww")
        assert len(results) == 3

    def test_get_user_playlists(self, yt, yt_auth):
        channel = "UCPVhZsC2od1xjGhgEc2NEPQ"  # Vevo playlists
        user = yt_auth.get_user(channel)
        results = yt_auth.get_user_playlists(channel, user["playlists"]["params"])
        assert len(results) > 100

        results_empty = yt.get_user_playlists(channel, user["playlists"]["params"])
        assert len(results_empty) == 0

    def test_get_user_videos(self, yt, yt_auth):
        channel = "UCus8EVJ7Oc9zINhs-fg8l1Q"  # Turbo
        user = yt_auth.get_user(channel)
        results = yt_auth.get_user_videos(channel, user["videos"]["params"])
        assert len(results) > 100

        results_empty = yt.get_user_videos(channel, user["videos"]["params"])
        assert len(results_empty) == 0

    def test_get_album_browse_id(self, yt, sample_album):
        warnings.filterwarnings(action="ignore", category=DeprecationWarning)
        browse_id = yt.get_album_browse_id("OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY")
        assert browse_id == sample_album

    def test_get_album_browse_id_issue_470(self, yt):
        escaped_browse_id = yt.get_album_browse_id("OLAK5uy_nbMYyrfeg5ZgknoOsOGBL268hGxtcbnDM")
        assert escaped_browse_id == "MPREb_pZhPA6GfQmN"

    def test_get_album_2024(self, yt):
        with open(Path(__file__).parent.parent / "data" / "2024_03_get_album.json", encoding="utf8") as f:
            mock_response = json.load(f)
        with mock.patch("ytmusicapi.YTMusic._send_request", return_value=mock_response):
            album = yt.get_album("MPREabc")
            assert len(album["tracks"]) == 19
            assert len(album["artists"]) == 1
            assert len(album) == 14
            for track in album["tracks"]:
                assert isinstance(track["title"], str) and track["title"]
                assert len(track["artists"]) > 0
                for artist in track["artists"]:
                    assert "name" in artist
                    assert isinstance(artist["name"], str) and artist["name"]

    def test_get_album(self, yt, yt_auth, sample_album):
        album = yt_auth.get_album(sample_album)
        assert len(album) >= 9
        assert "isExplicit" in album
        assert album["tracks"][0]["isExplicit"]
        assert all(item["views"] is not None for item in album["tracks"])
        assert all(item["album"] is not None for item in album["tracks"])
        assert album["likeStatus"] is not None
        assert album["audioPlaylistId"] is not None
        assert album["tracks"][0]["trackNumber"] == 1
        assert "feedbackTokens" in album["tracks"][0]
        album = yt.get_album("MPREb_BQZvl3BFGay")
        assert album["audioPlaylistId"] is not None
        assert len(album["tracks"]) == 7
        assert len(album["tracks"][0]["artists"]) == 1
        album = yt.get_album("MPREb_rqH94Zr3NN0")
        assert album["likeStatus"] is not None
        assert album["audioPlaylistId"] is not None
        assert len(album["tracks"][0]["artists"]) == 2
        album = yt.get_album("MPREb_TPH4WqN5pUo")  # album with tracks completely removed/missing
        assert album["likeStatus"] is not None
        assert album["audioPlaylistId"] is not None
        assert album["tracks"][0]["trackNumber"] == 3
        assert album["tracks"][13]["trackNumber"] == 18
        album = yt.get_album("MPREb_YuigcYm2erf")  # album with track (#8) disabled/greyed out
        assert album["likeStatus"] is not None
        assert album["audioPlaylistId"] is not None
        assert album["tracks"][7]["trackNumber"] is None

    def test_get_album_errors(self, yt):
        with pytest.raises(Exception, match="Invalid album browseId"):
            yt.get_album("asdf")

    def test_get_album_other_versions(self, yt):
        # Eminem - Curtain Call: The Hits (Explicit Variant)
        album = yt.get_album("MPREb_LQCAymzbaKJ")
        variants = album["other_versions"]
        assert len(variants) >= 1  # appears to be regional
        variant = variants[0]
        assert variant["type"] == "Album"
        assert len(variant["artists"]) == 1
        assert variant["artists"][0] == {"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}
        assert variant["audioPlaylistId"] is not None

        # album that's multi-artist, a single, and has clean version
        # Cassö & RAYE - Prada
        album = yt.get_album("MPREb_of3qfisa0yU")
        assert not album["isExplicit"]
        variant = album["other_versions"][0]
        assert variant["type"] == "Single"
        assert variant["isExplicit"]
        assert len(variant["artists"]) == 3
        assert variant["artists"][0]["id"] == "UCGWMNnI1Ky5bMcRlr73Cj2Q"
        assert variant["artists"][1]["name"] == "RAYE"
        assert variant["artists"][2] == {"id": "UCb7jnkQW94hzOoWkG14zs4w", "name": "D-Block Europe"}

    def test_get_song(self, config, yt, yt_oauth, sample_video):
        song = yt_oauth.get_song(config["uploads"]["private_upload_id"])  # private upload
        assert len(song) == 5
        song = yt.get_song(sample_video)
        if not is_ci():  # skip assert on GitHub CI because it doesn't work for some reason
            assert len(song["streamingData"]["adaptiveFormats"]) >= 10

    def test_get_song_related_content(self, yt_oauth, sample_video):
        song = yt_oauth.get_watch_playlist(sample_video)
        song = yt_oauth.get_song_related(song["related"])
        assert len(song) >= 5

    def test_get_lyrics(self, config, yt, sample_video):
        playlist = yt.get_watch_playlist(sample_video)
        # test normal lyrics
        lyrics_song = yt.get_lyrics(playlist["lyrics"])
        assert lyrics_song is not None
        assert isinstance(lyrics_song["lyrics"], str)
        assert lyrics_song["hasTimestamps"] is False

        # test lyrics with timestamps
        lyrics_song = yt.get_lyrics(playlist["lyrics"], timestamps=True)
        assert lyrics_song is not None
        assert len(lyrics_song["lyrics"]) >= 1
        assert lyrics_song["hasTimestamps"] is True

        # check the LyricLine object
        song = lyrics_song["lyrics"][0]
        assert isinstance(song, LyricLine)
        assert isinstance(song.text, str)
        assert song.start_time <= song.end_time
        assert isinstance(song.id, int)

        playlist = yt.get_watch_playlist(config["uploads"]["private_upload_id"])
        assert playlist["lyrics"] is None
        with pytest.raises(Exception):
            yt.get_lyrics(playlist["lyrics"])

    def test_get_signatureTimestamp(self, yt):
        signature_timestamp = yt.get_signatureTimestamp()
        assert signature_timestamp is not None

    def test_set_tasteprofile(self, yt_brand):
        with pytest.raises(Exception):
            yt_brand.set_tasteprofile(["test", "test2"])
        taste_profile = yt_brand.get_tasteprofile()
        assert yt_brand.set_tasteprofile(list(taste_profile)[:1], taste_profile) is None

    def test_get_tasteprofile(self, yt, yt_oauth):
        result = yt_oauth.get_tasteprofile()
        assert len(result) >= 0

    def test_get_search_suggestions(self, yt, yt_brand, yt_auth):
        result = yt.get_search_suggestions("fade")
        assert len(result) >= 0

        result = yt.get_search_suggestions("fade", detailed_runs=True)
        assert len(result) >= 0

        # add search term to history
        first_pass = yt_brand.search("b")
        assert len(first_pass) > 0

        # get results
        results = yt_auth.get_search_suggestions("b", detailed_runs=True)
        assert len(results) > 0
        assert any(not item["fromHistory"] for item in results)
