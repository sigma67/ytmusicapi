from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.podcasts import *
from ytmusicapi.parsers.songs import *
from ytmusicapi.type_alias import JsonDict

TRENDS = {"ARROW_DROP_UP": "up", "ARROW_DROP_DOWN": "down", "ARROW_CHART_NEUTRAL": "neutral"}


def parse_chart_song(data: JsonDict) -> JsonDict:
    parsed = parse_trending_song(data)
    parsed.update(parse_ranking(data))
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
    parsed.update(parse_ranking(data))
    return parsed


def parse_trending_song(data: JsonDict) -> JsonDict:
    flex_0 = get_flex_column_item(data, 0)
    return {
        "title": nav(flex_0, TEXT_RUN_TEXT),
        "videoId": nav(flex_0, TEXT_RUN + NAVIGATION_VIDEO_ID, True),
        **(parse_song_runs(nav(get_flex_column_item(data, 1), TEXT_RUNS))),
        "playlistId": nav(flex_0, TEXT_RUN + NAVIGATION_PLAYLIST_ID, True),
        "thumbnails": nav(data, THUMBNAILS),
        "isExplicit": nav(data, BADGE_LABEL, True) is not None,
    }


def parse_ranking(data: JsonDict) -> JsonDict:
    return {
        "rank": nav(data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *TEXT_RUN_TEXT]),
        "trend": TRENDS[nav(data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *ICON_TYPE])],
    }
