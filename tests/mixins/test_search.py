from typing import Any

import pytest

from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.parsers.search import ALL_RESULT_TYPES, API_RESULT_TYPES


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
            (
                "Eminem Houdini",
                {
                    "title": "Houdini",
                    "artists": [{"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}],
                    "type": "Single",
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
        assert all(item["views"] != "" for item in results)
        assert all(item["resultType"] == "video" for item in results)
        results = yt_auth.search(query, filter="albums", limit=40)
        assert len(results) > 20
        assert all(item["resultType"] == "album" for item in results)
        results = yt_auth.search("armen van buren", filter="artists", ignore_spelling=True)
        assert len(results) < 5
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

    def test_search_top_result(self, yt):
        results = yt.search("fdsfsfsd")  # issue 524
        assert results[0]["category"] == "Top result"
        assert results[0]["resultType"] == "playlist"
        assert results[0]["playlistId"].startswith("PL")
        assert len(results[0]["author"]) > 0

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
        with pytest.raises(Exception):
            yt_oauth.search("beatles", filter="community_playlists", scope="library", limit=40)
        with pytest.raises(Exception):
            yt_oauth.search("beatles", filter="featured_playlists", scope="library", limit=40)

    def test_remove_search_suggestions_valid(self, yt_auth):
        first_pass = yt_auth.search("b")  # Populate the suggestion history
        assert len(first_pass) > 0, "Search returned no results"

        results = yt_auth.get_search_suggestions("b", detailed_runs=True)
        assert len(results) > 0, "No search suggestions returned"
        assert any(item.get("fromHistory") for item in results), "No suggestions from history found"

        response = yt_auth.remove_search_suggestions(results)
        assert response is True, "Failed to remove search suggestions"

    def test_remove_search_suggestions_errors(self, yt_auth, yt):
        first_pass = yt_auth.search("a")
        assert len(first_pass) > 0, "Search returned no results"

        results = yt_auth.get_search_suggestions("a", detailed_runs=True)
        assert len(results) > 0, "No search suggestions returned"
        assert any(item.get("fromHistory") for item in results), "No suggestions from history found"

        suggestion_to_remove = [99]
        with pytest.raises(YTMusicUserError, match="Index out of range."):
            yt_auth.remove_search_suggestions(results, suggestion_to_remove)

        suggestion_to_remove = [0]
        with pytest.raises(YTMusicUserError, match="No search result from history provided."):
            results = yt.get_search_suggestions("a", detailed_runs=True)
            yt.remove_search_suggestions(results, suggestion_to_remove)
