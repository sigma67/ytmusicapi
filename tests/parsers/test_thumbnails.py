"""Parsers must tolerate items without thumbnail data (see #977)."""

import pytest

from ytmusicapi.parsers.browsing import (
    parse_album,
    parse_related_artist,
    parse_single,
    parse_song,
    parse_watch_playlist,
)
from ytmusicapi.parsers.explore import parse_chart_playlist
from ytmusicapi.parsers.library import parse_albums
from ytmusicapi.parsers.playlists import parse_playlist_header_meta
from ytmusicapi.parsers.podcasts import parse_base_header, parse_podcast
from ytmusicapi.parsers.watch import parse_watch_track


def _title(text: str = "Title", browse_id: str | None = None, video_id: str | None = None) -> dict:
    run: dict = {"text": text}
    if browse_id:
        run["navigationEndpoint"] = {"browseEndpoint": {"browseId": browse_id}}
    if video_id:
        run["navigationEndpoint"] = {"watchEndpoint": {"videoId": video_id}}
    return {"title": {"runs": [run]}}


def _subtitle(*texts: str) -> dict:
    return {"subtitle": {"runs": [{"text": text} for text in texts]}}


@pytest.mark.parametrize(
    ("parse_func", "item"),
    [
        (parse_album, {**_title(browse_id="MPREb_1"), **_subtitle("Album", " • ", "2024")}),
        (parse_single, {**_title(browse_id="MPREb_1"), **_subtitle("2024")}),
        (
            parse_song,
            {
                **_title(),
                **_subtitle("Artist"),
                "navigationEndpoint": {"watchEndpoint": {"videoId": "videoId1"}},
            },
        ),
        (parse_related_artist, {**_title(browse_id="UC_1"), **_subtitle("1M subscribers")}),
        (
            parse_watch_playlist,
            {**_title(), "navigationEndpoint": {"watchPlaylistEndpoint": {"playlistId": "RD1"}}},
        ),
        (parse_chart_playlist, _title(browse_id="VLPL1")),
        (parse_podcast, {**_title(browse_id="MPSP1"), **_subtitle("Channel")}),
        (parse_base_header, {**_title(), "straplineTextOne": {}}),
        (parse_playlist_header_meta, {**_title(), "secondSubtitle": {}}),
    ],
)
def test_missing_thumbnails(parse_func, item):
    assert parse_func(item)["thumbnails"] is None


def test_missing_thumbnails_library_albums():
    item = {"musicTwoRowItemRenderer": {**_title(browse_id="MPREb_1"), "subtitle": {}}}

    assert parse_albums([item])[0]["thumbnails"] is None


def test_missing_thumbnail_watch_track():
    track = {
        "videoId": "videoId1",
        **_title(),
        "menu": {"menuRenderer": {"items": []}},
        "longBylineText": {"runs": [{"text": "Artist"}]},
    }

    assert parse_watch_track(track)["thumbnail"] is None
