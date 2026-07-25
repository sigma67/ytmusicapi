import pytest

from ytmusicapi.parsers.constants import DOT_SEPARATOR_RUN
from ytmusicapi.parsers.songs import parse_song_run, parse_song_runs

DOT = DOT_SEPARATOR_RUN


def _linked(name: str, browse_id: str) -> dict:
    return {"text": name, "navigationEndpoint": {"browseEndpoint": {"browseId": browse_id}}}


class TestParseSongRuns:
    def test_skip_type_spec_before_artist(self):
        runs = [{"text": "Song"}, DOT, _linked("Eminem", "UCedvOgsKFzcK3hA5taf3KoQ"), DOT, {"text": "2:16"}]
        parsed = parse_song_runs(runs, skip_type_spec=True)
        assert parsed["artists"] == [{"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}]

    def test_skip_type_spec_when_song_has_no_artist(self):
        # artist-less song: "Song • 2:16 • 5.4K plays" must not leak "Song" as an artist
        runs = [{"text": "Song"}, DOT, {"text": "2:16"}, {"text": ""}, {"text": "5.4K plays"}]
        parsed = parse_song_runs(runs, skip_type_spec=True)
        assert "artists" not in parsed
        assert parsed["duration"] == "2:16"
        assert parsed["views"] == "5.4K"

    def test_linked_leading_artist_is_not_stripped(self):
        # no type spec: a linked artist in the first run must survive
        runs = [_linked("Eminem", "UCedvOgsKFzcK3hA5taf3KoQ"), DOT, {"text": "2:16"}]
        parsed = parse_song_runs(runs, skip_type_spec=True)
        assert parsed["artists"] == [{"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}]


class TestParseSongRun:
    # all view count strings below are verbatim API responses for the respective language
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("1.7B views", "1.7B"),
            ("1,234,567 views", "1,234,567"),
            ("340 views", "340"),
            ("1,7\xa0Mrd. Aufrufe", "1,7\xa0Mrd."),
            ("125.459 Aufrufe", "125.459"),
            ("109\xa0тыс. просмотров", "109\xa0тыс."),  # noqa: RUF001
            ("1,7\xa0Md de vues", "1,7\xa0Md"),
            ("88\xa0k\xa0vues", "88\xa0k"),
            ("2\xa0M de visualizaciones", "2\xa0M"),
            ("6,1\xa0Mln di visualizzazioni", "6,1\xa0Mln"),
            ("3406万回視聴", "3406万回視聴"),
            ("747万次观看", "747万次观看"),
            ("1.7\xa0مليار", "1.7\xa0مليار"),  # noqa: RUF001
            ("74\xa0लाख", "74\xa0लाख"),
        ],
    )
    def test_views(self, text, expected):
        assert parse_song_run({"text": text}) == {"type": "views", "data": expected}

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("조회수 17억회", "17억회"),
            ("조회수 340회", "340회"),
            ("觀看次數：17億次", "17億次"),  # noqa: RUF001
            ("播放次數：4505", "4505"),  # noqa: RUF001
            ("播放次数：3908万", "3908万"),  # noqa: RUF001
            ("再生回数 4.3億 回", "4.3億"),
            ("‫3.5\xa0ارب بار چلائے گئے", "3.5\xa0ارب"),  # noqa: RUF001
        ],
    )
    def test_views_with_leading_word(self, text, expected):
        assert parse_song_run({"text": text}) == {"type": "views", "data": expected}

    @pytest.mark.parametrize(
        "text", ["2Pac", "21", "6ix9ine", "AKB48", "乃木坂46", "22/7", "The Wolfpack & Reel Wolf"]
    )
    def test_unlinked_artist(self, text):
        assert parse_song_run({"text": text}) == {"type": "artist", "data": {"name": text, "id": None}}

    @pytest.mark.parametrize(
        ("text", "expected_type"), [("3:48", "duration"), ("1:23:45", "duration"), ("2020", "year")]
    )
    def test_duration_and_year(self, text, expected_type):
        assert parse_song_run({"text": text}) == {"type": expected_type, "data": text}
