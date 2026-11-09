import pytest
from pydantic import field_serializer

from tests.model_helpers import assert_response_model
from ytmusicapi.models import YTMusicModel


class Item(YTMusicModel):
    title: str
    count: int | None = None


class Collection(YTMusicModel):
    tracks: list[Item]


def test_accepts_nested_models_defaults_and_extra_fields() -> None:
    response = Collection.model_validate({"tracks": [{"title": "Song"}], "newField": "kept"})

    assert_response_model(
        response, Collection, {"tracks": [{"title": "Song", "count": None}], "newField": "kept"}
    )


@pytest.mark.parametrize("response", [{"title": "Song", "count": None}, Collection(tracks=[])])
def test_rejects_a_dictionary_or_wrong_model(response: object) -> None:
    with pytest.raises(AssertionError, match="Expected Item"):
        assert_response_model(response, Item, {"title": "Song", "count": None})


@pytest.mark.parametrize(
    "expected",
    [
        {"title": "Different", "count": None},
        {"title": "Song"},
        {"title": "Song", "count": 1},
        {"title": "Song", "count": None, "unexpected": True},
    ],
)
def test_rejects_changed_or_missing_fields(expected: dict[str, object]) -> None:
    with pytest.raises(AssertionError, match="Response fields differ"):
        assert_response_model(Item(title="Song"), Item, expected)


def test_rejects_a_lossy_json_round_trip() -> None:
    class LossyItem(Item):
        @field_serializer("title", when_used="json")
        def serialize_title(self, value: str) -> str:
            return value.lower()

    with pytest.raises(AssertionError, match="JSON round-trip changed response"):
        assert_response_model(LossyItem(title="Song"), LossyItem, {"title": "Song", "count": None})
