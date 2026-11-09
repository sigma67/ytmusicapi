"""Assertions shared by offline response-model and parser tests."""

from typing import Any

from ytmusicapi.models import YTMusicModel


def assert_response_model(response: object, model_type: type[YTMusicModel], expected: dict[str, Any]) -> None:
    """Check a parser result against independently specified model contents.

    Include every field, including defaults and extra fields, in ``expected``.
    Nested models are represented by dictionaries, as in ``model_dump()``.
    Assert nested model types and endpoint-specific behavior in the calling test.
    """
    assert isinstance(response, model_type), f"Expected {model_type.__name__}, got {type(response).__name__}"
    assert response.model_dump() == expected, "Response fields differ from the expected contents"
    assert model_type.model_validate_json(response.model_dump_json()) == response, (
        "JSON round-trip changed response"
    )
