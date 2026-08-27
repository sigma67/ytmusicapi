from ytmusicapi.parsers.search import parse_search_result


def _flex_result(**extra: str) -> dict:
    result = {
        "flexColumns": [
            {"musicResponsiveListItemFlexColumnRenderer": {"text": {"runs": [{"text": "Song Title"}]}}},
            {"musicResponsiveListItemFlexColumnRenderer": {"text": {"runs": [{"text": "Artist"}]}}},
        ],
    }
    result.update(extra)
    return result


class TestParseSearchResultIsAvailable:
    def test_defaults_to_available(self):
        parsed = parse_search_result(_flex_result(), "song", "Songs")
        assert parsed["isAvailable"] is True

    def test_grey_out_policy_marks_unavailable(self):
        parsed = parse_search_result(
            _flex_result(musicItemRendererDisplayPolicy="MUSIC_ITEM_RENDERER_DISPLAY_POLICY_GREY_OUT"),
            "video",
            "Videos",
        )
        assert parsed["isAvailable"] is False

    def test_other_policy_values_remain_available(self):
        parsed = parse_search_result(
            _flex_result(musicItemRendererDisplayPolicy="MUSIC_ITEM_RENDERER_DISPLAY_POLICY_DEFAULT"),
            "song",
            "Songs",
        )
        assert parsed["isAvailable"] is True

    def test_other_result_types_are_unaffected(self):
        # isAvailable is only meaningful for playable song/video results
        parsed = parse_search_result(_flex_result(), "album", "Albums")
        assert "isAvailable" not in parsed
