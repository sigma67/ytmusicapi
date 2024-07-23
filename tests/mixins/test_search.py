import pytest

from ytmusicapi import YTMusic
from ytmusicapi.parsers.search import ALL_RESULT_TYPES


class TestSearch:
    def test_search_exceptions(self, yt_auth):
        query = "edm playlist"
        with pytest.raises(Exception, match="Invalid filter provided"):
            yt_auth.search(query, filter="song")
        with pytest.raises(Exception, match="Invalid scope provided"):
            yt_auth.search(query, scope="upload")

    @pytest.mark.parametrize("query", ["Monekes", "llwlwl", "heun"])
    def test_search_queries(self, yt, yt_brand, query: str) -> None:
        results = yt_brand.search(query)
        assert ["resultType" in r for r in results] == [True] * len(results)
        assert len(results) >= 5
        assert not any(
            artist["name"].lower() in ALL_RESULT_TYPES
            for result in results
            if "artists" in result
            for artist in result["artists"]
        )
        results = yt.search(query)
        assert len(results) >= 5
        assert not any(
            artist["name"].lower() in ALL_RESULT_TYPES
            for result in results
            if "artists" in result
            for artist in result["artists"]
        )

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
        assert all(item["resultType"] == "song" for item in results)
        results = yt_auth.search(query, filter="videos")
        assert len(results) > 10
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
        assert len(results) > 10
        assert all(item["resultType"] == "podcast" for item in results)
        results = yt_auth.search(query, filter="episodes")
        assert len(results) >= 5
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
