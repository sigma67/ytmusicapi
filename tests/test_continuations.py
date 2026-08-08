from ytmusicapi.continuations import get_validated_continuations_2025
from ytmusicapi.type_alias import JsonDict, JsonList


def _make_page(video_ids: list[int], next_token: str | None) -> JsonDict:
    """Build a fake YouTube Music continuation response."""
    continuation_items: JsonList = [{"videoId": video_id} for video_id in video_ids]
    if next_token is not None:
        continuation_items.append(
            {
                "continuationItemRenderer": {
                    "continuationEndpoint": {"continuationCommand": {"token": next_token}}
                }
            }
        )
    return {
        "onResponseReceivedActions": [
            {"appendContinuationItemsAction": {"continuationItems": continuation_items}}
        ]
    }


def _parse_func(continuation_items: JsonList) -> JsonList:
    return [item for item in continuation_items if "videoId" in item]


def _initial_results(first_token: str) -> JsonDict:
    return {
        "contents": [
            {"videoId": 0},
            {
                "continuationItemRenderer": {
                    "continuationEndpoint": {"continuationCommand": {"token": first_token}}
                }
            },
        ]
    }


class TestValidatedContinuations2025:
    def test_retries_short_pages(self) -> None:
        """A continuation page that returns too few items is retried until it is complete."""
        t1_calls = 0

        def request_func(body: JsonDict) -> JsonDict:
            nonlocal t1_calls
            token = body["continuation"]
            if token == "T1":
                t1_calls += 1
                if t1_calls == 1:
                    return _make_page([1], "T2")  # short response, must be retried
                return _make_page([1, 2, 3], "T2")
            if token == "T2":
                return _make_page([4, 5, 6], None)  # last page, no further continuation
            raise AssertionError(f"unexpected token {token}")

        items = get_validated_continuations_2025(
            _initial_results("T1"), limit=6, per_page=3, request_func=request_func, parse_func=_parse_func
        )

        assert [item["videoId"] for item in items] == [1, 2, 3, 4, 5, 6]
        assert t1_calls == 2  # first attempt was short and retried once

    def test_gives_up_after_max_retries(self) -> None:
        """If a page never returns enough items, retries are capped and partial results are returned."""
        calls = 0

        def request_func(body: JsonDict) -> JsonDict:
            nonlocal calls
            calls += 1
            return _make_page([1], None)  # always short, no next token

        items = get_validated_continuations_2025(
            _initial_results("T1"),
            limit=3,
            per_page=3,
            request_func=request_func,
            parse_func=_parse_func,
            max_retries=2,
        )

        assert [item["videoId"] for item in items] == [1]
        assert calls == 3  # 1 initial attempt + 2 retries

    def test_stops_at_limit(self) -> None:
        """No continuation request is sent once the limit is reached."""

        def request_func(body: JsonDict) -> JsonDict:
            token = body["continuation"]
            if token == "T1":
                return _make_page([1, 2, 3], "T2")
            raise AssertionError("continuation past the limit should not be requested")

        items = get_validated_continuations_2025(
            _initial_results("T1"), limit=3, per_page=3, request_func=request_func, parse_func=_parse_func
        )

        assert [item["videoId"] for item in items] == [1, 2, 3]
