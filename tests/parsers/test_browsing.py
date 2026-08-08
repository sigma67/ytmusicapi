from copy import deepcopy

import pytest

from tests.parsers.data import OWNED_PLAYLIST
from ytmusicapi.navigation import MRLIR, MTRIR
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist


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
