import pytest

from ytmusicapi.navigation import MRLIR, MTRIR
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist


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
