import time
from typing import Any

import pytest

from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.navigation import MRLIR
from ytmusicapi.parsers.search import ALL_RESULT_TYPES, API_RESULT_TYPES

STANFORD_PODCAST_SEARCH_QUERY = 'intitle:"109. Simplify!" before:2024-01-01 after:2023-01-01'


class TestSearch:
    def test_search_exceptions(self, yt_auth):
        query = "edm playlist"
        with pytest.raises(Exception, match="Invalid filter provided"):
            yt_auth.search(query, filter="song")
        with pytest.raises(Exception, match="Invalid scope provided"):
            yt_auth.search(query, scope="upload")

    @pytest.mark.parametrize("query", ["Monekes", "llwlwl", "heun"])
    @pytest.mark.parametrize("yt_instance", ["yt", "yt_brand"])
    def test_search_queries(self, query: str, yt_instance: str, request: pytest.FixtureRequest) -> None:
        yt: YTMusic = request.getfixturevalue(yt_instance)
        results = yt.search(query)
        assert all(album["playlistId"] is not None for album in results if album["resultType"] == "album")
        assert ["resultType" in r for r in results] == [True] * len(results)
        assert len(results) >= 5
        assert not any(
            artist["name"].lower() in API_RESULT_TYPES
            for result in results
            if "artists" in result
            for artist in result["artists"]
        )

    @pytest.mark.parametrize(
        "case",
        [
            (  # this test should be a single, but YTM currently doesn't find singles with album search 🤡
                "eminem relapse",
                {
                    "title": "Relapse",
                    "artists": [{"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}],
                    "type": "Album",
                    "resultType": "album",
                },
            ),
            (
                "Seven Martin Garrix",
                {
                    "title": "Seven",
                    "artists": [{"name": "Martin Garrix", "id": "UCqJnSdHjKtfsrHi9aI-9d3g"}],
                    "type": "EP",
                    "resultType": "album",
                },
            ),
        ],
    )
    def test_search_album_artists(self, yt, case: tuple[str, dict[str, Any]]):
        (query, expected) = case
        results = yt.search(query, filter="albums")

        assert any(result == result | expected for result in results)

    def test_search_ignore_spelling(self, yt_auth):
        results = yt_auth.search("Martin Stig Andersen - Deteriation", ignore_spelling=True)
        assert len(results) > 0

    def test_search_localized(self):
        yt_local = YTMusic(language="it")
        results = yt_local.search("ABBA")
        assert all(result["resultType"] in ALL_RESULT_TYPES for result in results)
        assert len([x for x in results if x["resultType"] == "album"]) <= 10  # album is default fallback

        results = yt_local.search("ABBA", filter="songs")
        assert all(item["resultType"] == "song" for item in results)

    def test_search_filters(self, yt_auth):
        query = "hip hop playlist"
        results = yt_auth.search(query, filter="songs")
        assert len(results) > 10
        assert all(item["views"] != "" for item in results)
        assert all(len(item["artists"]) > 0 for item in results)
        assert all(item["resultType"] == "song" for item in results)
        results = yt_auth.search(query, filter="videos")
        assert len(results) > 10
        assert all(
            item["views"] != "" for item in results if item["videoType"] != "MUSIC_VIDEO_TYPE_PODCAST_EPISODE"
        )  # video results include podcast episodes, which can't track views
        assert all(item["resultType"] == "video" for item in results)
        results = yt_auth.search(query, filter="albums", limit=40)
        assert len(results) > 20
        assert all(item["resultType"] == "album" for item in results)
        results = yt_auth.search("armen van buren", filter="artists", ignore_spelling=True)
        # without ignore_spelling the query is corrected to "armin van buuren", matching far more artists
        assert len(results) < len(yt_auth.search("armen van buren", filter="artists"))
        assert all(item["resultType"] == "artist" for item in results)
        results = yt_auth.search("classical music", filter="playlists")
        assert len(results) > 10
        assert all(item["resultType"] == "playlist" for item in results)
        results = yt_auth.search("clasical music", filter="playlists", ignore_spelling=True)
        assert len(results) > 10
        results = yt_auth.search("clasic rock", filter="community_playlists", ignore_spelling=True)
        assert len(results) > 10
        assert all(item["resultType"] == "playlist" for item in results)
        results = yt_auth.search("hip hop", filter="featured_playlists")
        assert len(results) > 10
        assert all(item["resultType"] == "playlist" for item in results)
        results = yt_auth.search("some user", filter="profiles")
        assert len(results) > 10
        assert all(item["resultType"] == "profile" for item in results)
        results = yt_auth.search(query, filter="podcasts")
        assert len(results) > 5
        assert all(item["resultType"] == "podcast" for item in results)
        results = yt_auth.search(query, filter="episodes")
        assert len(results) >= 3
        assert all(item["resultType"] == "episode" for item in results)

    def test_search_playlist_return_correct_item_count(self, yt: YTMusic):
        results = yt.search(query="Best Phonk music", filter="community_playlists")
        assert all(item["itemCount"] is None for item in results)

        results = yt.search(query="Best Phonk music", filter="featured_playlists")
        assert all((item["itemCount"] is not None and isinstance(item["itemCount"], int)) for item in results)

    def test_search_episode_category(self, yt_auth):
        """Test resultType detection for episodes by searching for a podcast without a filter."""
        results = yt_auth.search(STANFORD_PODCAST_SEARCH_QUERY)
        episode = next(
            item
            for item in results
            if "podcast" in item and item["podcast"]["name"] == "Stanford GSB Podcasts"
        )
        assert episode["resultType"] == "episode"
        assert episode["podcast"]["id"] == "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9"

    def test_search_top_result_playlist(self, yt_oauth):
        results = yt_oauth.search('intitle:"grace OST" playlist')  # issue 524
        assert results[0]["category"] == "Top result"
        assert results[0]["resultType"] == "playlist"
        assert results[0]["playlistId"].startswith("PL")
        assert len(results[0]["author"]) > 0

    def test_search_top_result_episode(self, yt):
        results = yt.search(STANFORD_PODCAST_SEARCH_QUERY)
        assert results[0]["category"] == "Top result"
        assert results[0]["resultType"] == "episode"
        assert results[0]["podcast"] == {
            "id": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9",
            "name": "Stanford GSB Podcasts",
        }

    def test_search_top_result_video(self, yt):
        results = yt.search("Fuel Eminem")
        assert results[0]["category"] == "Top result"
        assert results[0]["resultType"] == "video"
        assert results[0]["videoId"] == "t5H_CewqpKA"
        assert results[0]["artists"] == [
            {"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"},
            {"name": "JID", "id": "UCRlGNubLJBgW9VRCuiUnuYw"},
        ]

    def test_search_uploads(self, config, yt, yt_oauth):
        with pytest.raises(Exception, match="No filter can be set when searching uploads"):
            yt.search(
                config["queries"]["uploads_songs"],
                filter="songs",
                scope="uploads",
                limit=40,
            )
        results = yt_oauth.search(config["queries"]["uploads_songs"], scope="uploads", limit=40)
        assert len(results) > 20
        assert all(isinstance(item["title"], str) for item in results)
        assert all(item.get("browseId", None) or item.get("videoId", None) for item in results)
        assert all(len(item["thumbnails"]) >= 2 for item in results)

    def test_search_library(self, config, yt_oauth):
        results = yt_oauth.search(config["queries"]["library_any"], scope="library")
        assert len(results) > 5
        results = yt_oauth.search(
            config["queries"]["library_songs"], filter="songs", scope="library", limit=40
        )
        assert len(results) > 10
        results = yt_oauth.search(
            config["queries"]["library_albums"], filter="albums", scope="library", limit=40
        )
        assert len(results) >= 4
        results = yt_oauth.search(
            config["queries"]["library_artists"], filter="artists", scope="library", limit=40
        )
        assert len(results) >= 1
        results = yt_oauth.search(config["queries"]["library_playlists"], filter="playlists", scope="library")
        assert len(results) >= 1
        with pytest.raises(YTMusicUserError):
            yt_oauth.search("beatles", filter="community_playlists", scope="library", limit=40)
        with pytest.raises(YTMusicUserError):
            yt_oauth.search("beatles", filter="featured_playlists", scope="library", limit=40)

    def _flex_item(self, title: str) -> dict:
        return {
            MRLIR: {
                "flexColumns": [
                    {"musicResponsiveListItemFlexColumnRenderer": {"text": {"runs": [{"text": title}]}}},
                    {"musicResponsiveListItemFlexColumnRenderer": {"text": {"runs": [{"text": "Artist"}]}}},
                ]
            }
        }

    def _shelf_response(self, shelf_title: str, item_titles: list[str]) -> dict:
        return {
            "contents": {
                "sectionListRenderer": {
                    "contents": [
                        {
                            "musicShelfRenderer": {
                                "title": {"runs": [{"text": shelf_title}]},
                                "contents": [self._flex_item(title) for title in item_titles],
                            }
                        }
                    ]
                }
            }
        }

    def test_search_filtered_localized_shelf_title_is_matched(self, monkeypatch: pytest.MonkeyPatch):
        """Regression test for #1006.

        The shelf's category text is localized (e.g. Korean "앨범" for "Albums"),
        so matching a filter against it must go through the same gettext catalog
        used to translate the shelf title in the first place, rather than the
        raw English filter stem.
        """
        yt_ko = YTMusic(language="ko")
        response = self._shelf_response("앨범", ["Test Album"])
        monkeypatch.setattr(yt_ko, "_send_request", lambda endpoint, body, additionalParams="": response)

        results = yt_ko.search("test", filter="albums")

        assert len(results) == 1
        assert results[0]["resultType"] == "album"

    def test_search_filtered_mismatched_shelf_is_still_skipped(self, monkeypatch: pytest.MonkeyPatch):
        """A shelf that genuinely doesn't match the requested filter is still dropped."""
        yt_ko = YTMusic(language="ko")
        response = self._shelf_response("노래", ["Test Song"])  # "Songs", padded into an albums search
        monkeypatch.setattr(yt_ko, "_send_request", lambda endpoint, body, additionalParams="": response)

        results = yt_ko.search("test", filter="albums")

        assert results == []

    @pytest.mark.xdist_group("search_history")
    def test_remove_search_suggestions_valid(self, yt_auth):
        first_pass = yt_auth.search("be")  # Populate the suggestion history
        assert len(first_pass) > 0, "Search returned no results"
        time.sleep(5)
        results = yt_auth.get_search_suggestions("", detailed_runs=True)
        assert len(results) > 0, "No search suggestions returned"
        assert any(item.get("fromHistory") for item in results), "No suggestions from history found"

        response = yt_auth.remove_search_suggestions(results)
        assert response is True, "Failed to remove search suggestions"

    @pytest.mark.xdist_group("search_history")
    def test_remove_search_suggestions_errors(self, yt_auth, yt):
        first_pass = yt_auth.search("a")
        assert len(first_pass) > 0, "Search returned no results"
        time.sleep(5)  # wait for the search to reach the history

        results = yt_auth.get_search_suggestions("a", detailed_runs=True)
        assert len(results) > 0, "No search suggestions returned"
        assert any(item.get("fromHistory") for item in results), "No suggestions from history found"

        suggestion_to_remove = [99]
        with pytest.raises(YTMusicUserError, match="Index out of range"):
            yt_auth.remove_search_suggestions(results, suggestion_to_remove)

        suggestion_to_remove = [0]
        with pytest.raises(YTMusicUserError, match="No search result from history provided"):
            results = yt.get_search_suggestions("a", detailed_runs=True)
            yt.remove_search_suggestions(results, suggestion_to_remove)
