import pytest

from ytmusicapi.models.base import YTMusicModel


class Track(YTMusicModel):
    videoId: str
    title: str
    count: int | None = None


@pytest.fixture(name="track")
def fixture_track() -> Track:
    return Track(videoId="abc", title="Wonderwall")


class TestItemAccess:
    def test_getitem_returns_field_value(self, track: Track) -> None:
        assert track["title"] == "Wonderwall"

    def test_getitem_returns_none_for_unset_declared_field(self, track: Track) -> None:
        assert track["count"] is None

    def test_getitem_raises_keyerror_for_undeclared_field(self, track: Track) -> None:
        with pytest.raises(KeyError):
            track["nope"]

    def test_get_returns_field_value(self, track: Track) -> None:
        assert track.get("title") == "Wonderwall"

    def test_get_returns_none_for_unset_declared_field(self, track: Track) -> None:
        assert track.get("count") is None

    def test_get_returns_default_for_undeclared_field(self, track: Track) -> None:
        assert track.get("nope", "fallback") == "fallback"

    def test_get_defaults_to_none(self, track: Track) -> None:
        assert track.get("nope") is None

    def test_attribute_access_still_works(self, track: Track) -> None:
        assert track.title == "Wonderwall"


class TestContains:
    def test_declared_field_is_present(self, track: Track) -> None:
        assert "title" in track

    def test_unset_declared_field_is_still_present(self, track: Track) -> None:
        assert "count" in track

    def test_undeclared_field_is_absent(self, track: Track) -> None:
        assert "nope" not in track

    def test_non_string_key_is_absent(self, track: Track) -> None:
        assert 1 not in track


class TestMappingViews:
    def test_keys_are_in_declaration_order(self, track: Track) -> None:
        assert list(track.keys()) == ["videoId", "title", "count"]

    def test_values_include_none_for_unset_fields(self, track: Track) -> None:
        assert list(track.values()) == ["abc", "Wonderwall", None]

    def test_items_pair_keys_with_values(self, track: Track) -> None:
        assert list(track.items()) == [("videoId", "abc"), ("title", "Wonderwall"), ("count", None)]

    def test_iter_yields_keys_in_declaration_order(self, track: Track) -> None:
        assert list(track) == ["videoId", "title", "count"]

    def test_len_counts_every_declared_field(self, track: Track) -> None:
        assert len(track) == 3

    def test_dict_conversion_uses_the_mapping_protocol(self, track: Track) -> None:
        assert dict(track) == {"videoId": "abc", "title": "Wonderwall", "count": None}

    def test_double_star_unpacking(self, track: Track) -> None:
        assert {**track} == {"videoId": "abc", "title": "Wonderwall", "count": None}


class TestEquality:
    def test_equal_to_plain_dict_with_same_content(self, track: Track) -> None:
        assert track == {"videoId": "abc", "title": "Wonderwall", "count": None}

    def test_dict_on_the_left_is_also_equal(self, track: Track) -> None:
        assert {"videoId": "abc", "title": "Wonderwall", "count": None} == track

    def test_not_equal_to_dict_omitting_a_none_valued_field(self, track: Track) -> None:
        assert track != {"videoId": "abc", "title": "Wonderwall"}

    def test_not_equal_to_dict_with_different_value(self, track: Track) -> None:
        assert track != {"videoId": "abc", "title": "Champagne Supernova", "count": None}

    def test_equal_to_identical_model(self, track: Track) -> None:
        assert track == Track(videoId="abc", title="Wonderwall")

    def test_not_equal_to_different_model(self, track: Track) -> None:
        assert track != Track(videoId="xyz", title="Wonderwall")

    def test_not_equal_to_unrelated_type(self, track: Track) -> None:
        assert track != "Wonderwall"

    def test_nested_model_compares_against_nested_plain_dict(self) -> None:
        class Album(YTMusicModel):
            name: str
            track: Track

        album = Album(name="Morning Glory", track=Track(videoId="abc", title="Wonderwall"))
        assert album == {
            "name": "Morning Glory",
            "track": {"videoId": "abc", "title": "Wonderwall", "count": None},
        }

    def test_list_of_models_compares_against_list_of_dicts(self) -> None:
        class Playlist(YTMusicModel):
            tracks: list[Track]

        playlist = Playlist(tracks=[Track(videoId="abc", title="Wonderwall")])
        assert playlist == {"tracks": [{"videoId": "abc", "title": "Wonderwall", "count": None}]}


class TestExtraFields:
    @pytest.fixture(name="track_with_extra")
    def fixture_track_with_extra(self) -> Track:
        return Track(videoId="abc", title="Wonderwall", newFromYtm="surprise")  # type: ignore[call-arg]

    def test_undeclared_field_is_kept(self, track_with_extra: Track) -> None:
        assert track_with_extra["newFromYtm"] == "surprise"

    def test_undeclared_field_is_contained(self, track_with_extra: Track) -> None:
        assert "newFromYtm" in track_with_extra

    def test_undeclared_field_comes_after_declared_ones(self, track_with_extra: Track) -> None:
        assert list(track_with_extra.keys()) == ["videoId", "title", "count", "newFromYtm"]

    def test_undeclared_field_counts_towards_len(self, track_with_extra: Track) -> None:
        assert len(track_with_extra) == 4

    def test_undeclared_field_takes_part_in_dict_equality(self, track_with_extra: Track) -> None:
        assert track_with_extra == {
            "videoId": "abc",
            "title": "Wonderwall",
            "count": None,
            "newFromYtm": "surprise",
        }


class TestJsonRoundTrip:
    def test_model_dump_omits_nothing(self, track: Track) -> None:
        assert track.model_dump() == {"videoId": "abc", "title": "Wonderwall", "count": None}

    def test_parses_from_a_raw_dict(self) -> None:
        raw = {"videoId": "abc", "title": "Wonderwall"}
        assert Track(**raw) == {"videoId": "abc", "title": "Wonderwall", "count": None}


def test_exported_from_the_models_package() -> None:
    from ytmusicapi.models import YTMusicModel as Exported

    assert Exported is YTMusicModel
