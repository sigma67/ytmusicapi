from ytmusicapi.parsers.browsing import *
from ytmusicapi.type_alias import JsonDict

TRENDS = {"ARROW_DROP_UP": "up", "ARROW_DROP_DOWN": "down", "ARROW_CHART_NEUTRAL": "neutral"}


def parse_chart_song(data: JsonDict) -> JsonDict:
    parsed = parse_song_flat(data)
    parsed.update(parse_ranking(data))
    return parsed


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


def parse_chart_trending(data: JsonDict) -> JsonDict:
    flex_0 = get_flex_column_item(data, 0)
    artists = parse_song_artists(data, 1)
    index = get_dot_separator_index(artists)
    # last item is views for some reason
    views = None if index == len(artists) else artists.pop()["name"].split(" ")[0]
    return {
        "title": nav(flex_0, TEXT_RUN_TEXT),
        "videoId": nav(flex_0, TEXT_RUN + NAVIGATION_VIDEO_ID, True),
        "playlistId": nav(flex_0, TEXT_RUN + NAVIGATION_PLAYLIST_ID, True),
        "artists": artists,
        "thumbnails": nav(data, THUMBNAILS),
        "views": views,
    }


def parse_ranking(data: JsonDict) -> JsonDict:
    return {
        "rank": nav(data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *TEXT_RUN_TEXT]),
        "trend": TRENDS[nav(data, ["customIndexColumn", "musicCustomIndexColumnRenderer", *ICON_TYPE])],
    }
