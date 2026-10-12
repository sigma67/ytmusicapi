from copy import deepcopy

import pytest

from tests.parsers.data import OWNED_PLAYLIST
from ytmusicapi.navigation import MRLIR, MTRIR
from ytmusicapi.parsers.browsing import parse_content_list, parse_mixed_content, parse_playlist


def test_parse_playlist_marks_playlist_with_editor_endpoint_as_owned():
    playlist = parse_playlist(OWNED_PLAYLIST)

    assert playlist["owned"] is True


def test_parse_playlist_marks_playlist_without_editor_endpoint_as_not_owned():
    saved_playlist = deepcopy(OWNED_PLAYLIST)
    saved_playlist["menu"]["menuRenderer"]["items"][0]["menuNavigationItemRenderer"]["navigationEndpoint"] = {
        "watchPlaylistEndpoint": {"playlistId": "PL_family"}
    }

    playlist = parse_playlist(saved_playlist)

    assert playlist["owned"] is False


def _playlist_item(thumbnail_renderer: dict) -> dict:
    return {
        "title": {
            "runs": [
                {
                    "text": "My playlist",
                    "navigationEndpoint": {"browseEndpoint": {"browseId": "VLPLabc123"}},
                }
            ]
        },
        "subtitle": {"runs": [{"text": "Playlist"}]},
        **thumbnail_renderer,
    }


THUMBNAIL_RENDERER = {
    "thumbnailRenderer": {
        "musicThumbnailRenderer": {
            "thumbnail": {"thumbnails": [{"url": "https://example.com/t.jpg", "width": 1, "height": 1}]}
        }
    }
}


class TestParsePlaylist:
    def test_thumbnails(self):
        parsed = parse_playlist(_playlist_item(THUMBNAIL_RENDERER))
        assert parsed["playlistId"] == "PLabc123"
        assert parsed["thumbnails"] == [{"url": "https://example.com/t.jpg", "width": 1, "height": 1}]

    @pytest.mark.parametrize(
        "thumbnail_renderer",
        [
            {},
            {"thumbnailRenderer": {}},
            {"thumbnailRenderer": {"musicThumbnailRenderer": {}}},
            {"thumbnailRenderer": {"musicThumbnailRenderer": {"thumbnail": {}}}},
        ],
        ids=["absent", "empty_renderer", "empty_music_renderer", "empty_thumbnail"],
    )
    def test_missing_thumbnails(self, thumbnail_renderer):
        parsed = parse_playlist(_playlist_item(thumbnail_renderer))
        assert parsed["playlistId"] == "PLabc123"
        assert parsed["thumbnails"] is None


class TestParseContentList:
    def test_mixed_renderers_are_skipped(self):
        """A mood/genre carousel can mix renderer types; only the requested key is parsed."""
        results = [
            {MTRIR: {"id": 1}},
            {MRLIR: {"id": 2}},
            {MTRIR: {"id": 3}},
        ]

        assert parse_content_list(results, lambda item: item["id"], MTRIR) == [1, 3]
        assert parse_content_list(results, lambda item: item["id"], MRLIR) == [2]


class TestParseMixedContent:
    @pytest.mark.parametrize("include_unavailable", [False, True])
    def test_unavailable_upload_does_not_hide_other_recommendations(self, include_unavailable):
        artist_endpoint = {
            "browseEndpoint": {
                "browseId": "UCartist",
                "browseEndpointContextSupportedConfigs": {
                    "browseEndpointContextMusicConfig": {"pageType": "MUSIC_PAGE_TYPE_ARTIST"}
                },
            }
        }
        artist = {
            "title": {"runs": [{"text": "Artist", "navigationEndpoint": artist_endpoint}]},
            "subtitle": {},
            "navigationEndpoint": artist_endpoint,
        }
        song = {
            "title": {"runs": [{"text": "Song"}]},
            "subtitle": {"runs": [{"text": "Artist"}]},
            "navigationEndpoint": {"watchEndpoint": {"videoId": "video-id"}},
        }
        watch_playlist = {
            "title": {"runs": [{"text": "Radio"}]},
            "navigationEndpoint": {"watchPlaylistEndpoint": {"playlistId": "RDplaylist"}},
        }
        contents = [{MTRIR: artist}, {MTRIR: song}, {MTRIR: watch_playlist}]
        if include_unavailable:
            # #668: a deleted upload still appears in Listen again, but its
            # title has no navigation and its outer browse endpoint has no ID.
            unavailable = deepcopy(artist)
            unavailable["title"] = {"runs": [{"text": "Anthony M"}]}
            del unavailable["navigationEndpoint"]["browseEndpoint"]["browseId"]
            contents.insert(1, {MTRIR: unavailable})

        parsed = parse_mixed_content([{"musicCarouselShelfRenderer": {"contents": contents}}])

        assert parsed == [
            {
                "title": None,
                "contents": [
                    {"title": "Artist", "browseId": "UCartist", "subscribers": None, "thumbnails": None},
                    {
                        "title": "Song",
                        "videoId": "video-id",
                        "playlistId": None,
                        "thumbnails": None,
                        "artists": [{"name": "Artist", "id": None}],
                    },
                    {"title": "Radio", "playlistId": "RDplaylist", "thumbnails": None},
                ],
            }
        ]
