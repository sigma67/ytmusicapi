from ytmusicapi.parsers.playlists import parse_playlist_header_meta


def _header(**extra: dict) -> dict:
    header = {
        "title": {"runs": [{"text": "My Playlist"}]},
        "thumbnail": {
            "musicThumbnailRenderer": {
                "thumbnail": {"thumbnails": [{"url": "https://example.com/t.jpg", "width": 60, "height": 60}]}
            }
        },
    }
    header.update(extra)
    return header


class TestParsePlaylistHeaderMeta:
    def test_missing_second_subtitle(self):
        # some playlists are served without a secondSubtitle at all
        parsed = parse_playlist_header_meta(_header())
        assert parsed["title"] == "My Playlist"
        assert parsed["views"] is None
        assert parsed["duration"] is None
        assert parsed["trackCount"] is None

    def test_second_subtitle_track_count(self):
        parsed = parse_playlist_header_meta(
            _header(secondSubtitle={"runs": [{"text": "101 songs"}, {"text": " • "}, {"text": "6+ hours"}]})
        )
        assert parsed["trackCount"] == 101
        assert parsed["duration"] == "6+ hours"
