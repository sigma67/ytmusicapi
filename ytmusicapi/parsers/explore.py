from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.podcasts import *
from ytmusicapi.parsers.songs import *
from ytmusicapi.type_alias import JsonDict
from typing import Literal

TRENDS = {"ARROW_DROP_UP": "up", "ARROW_DROP_DOWN": "down", "ARROW_CHART_NEUTRAL": "neutral"}


def parse_chart_song(data: JsonDict) -> JsonDict:
    parsed = parse_song_flat(data)
    parsed.update(parse_ranking(data, none_if_absent=False))
    return parsed


def parse_chart_playlist(data: JsonDict) -> JsonDict:
    return {
        "title": nav(data, TITLE_TEXT),
        "playlistId": nav(data, TITLE + NAVIGATION_BROWSE_ID)[2:],
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }


def parse_chart_episode(data: JsonDict) -> JsonDict:
    episode = parse_episode(data)
    del episode["index"]
    episode["podcast"] = parse_id_name(nav(data, ["secondTitle", "runs", 0]))
    episode["duration"] = nav(data, SUBTITLE2, True)
    return episode


def parse_chart_artist(data: JsonDict) -> JsonDict:
    subscribers = get_flex_column_item(data, 1)
    if subscribers:
        subscribers = nav(subscribers, TEXT_RUN_TEXT).split(" ")[0]

    parsed = {
        "title": nav(get_flex_column_item(data, 0), TEXT_RUN_TEXT),
        "browseId": nav(data, NAVIGATION_BROWSE_ID),
        "subscribers": subscribers,
        "thumbnails": nav(data, THUMBNAILS),
    }
    parsed.update(parse_ranking(data, none_if_absent=True))
    return parsed


def parse_ranking(data: JsonDict, none_if_absent: Literal[True, False]) -> JsonDict:
    trend_icon_type = nav(
        data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *ICON_TYPE], none_if_absent
    )
    return {
        "rank": nav(
            data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *TEXT_RUN_TEXT], none_if_absent
        ),
        "trend": TRENDS[trend_icon_type] if trend_icon_type is not None else None,
    }
