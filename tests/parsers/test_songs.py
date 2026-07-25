from ytmusicapi.parsers.constants import DOT_SEPARATOR_RUN
from ytmusicapi.parsers.songs import parse_song_runs

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
