from ytmusicapi.type_alias import JsonDict, JsonList

from ..helpers import to_int
from ._utils import *
from .albums import parse_album_playlistid_if_exists
from .songs import *

ALL_RESULT_TYPES = [
    "album",
    "artist",
    "playlist",
    "song",
    "video",
    "station",
    "profile",
    "podcast",
    "episode",
]
API_RESULT_TYPES = ["single", "ep", *ALL_RESULT_TYPES]


def get_search_result_type(result_type_local: str, result_types_local: list[str]) -> str | None:
    if not result_type_local:
        return None
    result_type_local = result_type_local.lower()
    # default to album since it's labeled with multiple values ('Single', 'EP', etc.)
    if result_type_local not in result_types_local:
        result_type = "album"
    else:
        result_type = ALL_RESULT_TYPES[result_types_local.index(result_type_local)]

    return result_type


def parse_top_result(data: JsonDict, search_result_types: list[str]) -> JsonDict:
    result_type = get_search_result_type(nav(data, SUBTITLE), search_result_types)
    search_result = {"category": nav(data, CARD_SHELF_TITLE), "resultType": result_type}
    if result_type == "artist":
        subscribers = nav(data, SUBTITLE2, True)
        if subscribers:
            search_result["subscribers"] = subscribers.split(" ")[0]

        artist_info = parse_song_runs(nav(data, ["title", "runs"]))
        search_result.update(artist_info)

    if result_type in ["song", "video"]:
        on_tap = data.get("onTap")
        if on_tap:
            search_result["videoId"] = nav(on_tap, WATCH_VIDEO_ID)
            search_result["videoType"] = nav(on_tap, NAVIGATION_VIDEO_TYPE)

    if result_type in ["song", "video", "album"]:
        search_result["videoId"] = nav(data, ["onTap", *WATCH_VIDEO_ID], True)
        search_result["videoType"] = nav(data, ["onTap", *NAVIGATION_VIDEO_TYPE], True)

        search_result["title"] = nav(data, TITLE_TEXT)
        runs = nav(data, ["subtitle", "runs"])
        song_info = parse_song_runs(runs[2:])
        search_result.update(song_info)

    if result_type in ["album"]:
        search_result["browseId"] = nav(data, TITLE + NAVIGATION_BROWSE_ID, True)
        button_command = nav(data, ["buttons", 0, "buttonRenderer", "command"], True)
        search_result["playlistId"] = parse_album_playlistid_if_exists(button_command)

    if result_type in ["playlist"]:
        search_result["playlistId"] = nav(data, MENU_PLAYLIST_ID)
        search_result["title"] = nav(data, TITLE_TEXT)
        search_result["author"] = parse_song_artists_runs(nav(data, ["subtitle", "runs"])[2:])

    if result_type in ["episode"]:
        search_result["videoId"] = nav(data, [*THUMBNAIL_OVERLAY_NAVIGATION, *WATCH_VIDEO_ID])
        search_result["videoType"] = nav(data, [*THUMBNAIL_OVERLAY_NAVIGATION, *NAVIGATION_VIDEO_TYPE])
        runs = nav(data, SUBTITLE_RUNS)[2:]
        search_result["date"] = runs[0]["text"]
        search_result["podcast"] = parse_id_name(runs[2])

    search_result["thumbnails"] = nav(data, THUMBNAILS, True)
    return search_result


def parse_search_result(
    data: JsonDict, api_search_result_types: list[str], result_type: str | None, category: str | None
) -> JsonDict:
    default_offset = (not result_type or result_type == "album") * 2
    search_result: JsonDict = {"category": category}
    video_type = nav(data, [*PLAY_BUTTON, "playNavigationEndpoint", *NAVIGATION_VIDEO_TYPE], True)

    # determine result type based on browseId
    #  if there was no category title (i.e. for extra results in Top Result)
    if not result_type:
        if browse_id := nav(data, NAVIGATION_BROWSE_ID, True):
            mapping = {
                "VM": "playlist",
                "RD": "playlist",
                "VL": "playlist",
                "MPLA": "artist",
                "MPRE": "album",
                "MPSP": "podcast",
                "MPED": "episode",
                "UC": "artist",
            }
            result_type = next(
                iter(type for prefix, type in mapping.items() if browse_id.startswith(prefix)), None
            )
        else:
            result_type = {
                "MUSIC_VIDEO_TYPE_ATV": "song",
                "MUSIC_VIDEO_TYPE_PODCAST_EPISODE": "episode",
            }.get(video_type or "", "video")

    search_result["resultType"] = result_type

    if result_type != "artist":
        search_result["title"] = get_item_text(data, 0)

    if result_type == "artist":
        search_result["artist"] = get_item_text(data, 0)
        parse_menu_playlists(data, search_result)

    elif result_type == "album":
        search_result["type"] = get_item_text(data, 1)
        play_navigation = nav(data, [*PLAY_BUTTON, "playNavigationEndpoint"], True)
        search_result["playlistId"] = parse_album_playlistid_if_exists(play_navigation)

    elif result_type == "playlist":
        flex_item = nav(get_flex_column_item(data, 1), TEXT_RUNS)
        has_author = len(flex_item) == default_offset + 3
        search_result["itemCount"] = (get_item_text(data, 1, default_offset + has_author * 2) or "").split(
            " "
        )[0]
        if search_result["itemCount"] and search_result["itemCount"].isnumeric():
            search_result["itemCount"] = to_int(search_result["itemCount"])
        search_result["author"] = None if not has_author else get_item_text(data, 1, default_offset)

    elif result_type == "station":
        search_result["videoId"] = nav(data, NAVIGATION_VIDEO_ID)
        search_result["playlistId"] = nav(data, NAVIGATION_PLAYLIST_ID)

    elif result_type == "profile":
        search_result["name"] = get_item_text(data, 1, 2, True)

    elif result_type == "song":
        search_result["album"] = None
        if "menu" in data:
            toggle_menu = find_object_by_key(nav(data, MENU_ITEMS), TOGGLE_MENU)
            if toggle_menu:
                search_result["inLibrary"] = parse_song_library_status(toggle_menu)
                search_result["feedbackTokens"] = parse_song_menu_tokens(toggle_menu)

    elif result_type == "upload":
        browse_id = nav(data, NAVIGATION_BROWSE_ID, True)
        if not browse_id:  # song result
            flex_items = [nav(get_flex_column_item(data, i), ["text", "runs"], True) for i in range(2)]
            if flex_items[0]:
                search_result["videoId"] = nav(flex_items[0][0], NAVIGATION_VIDEO_ID, True)
                search_result["playlistId"] = nav(flex_items[0][0], NAVIGATION_PLAYLIST_ID, True)
            if flex_items[1]:
                search_result.update(parse_song_runs(flex_items[1]))
            search_result["resultType"] = "song"

        else:  # artist or album result
            search_result["browseId"] = browse_id
            if "artist" in search_result["browseId"]:
                search_result["resultType"] = "artist"
            else:
                flex_item2 = get_flex_column_item(data, 1)
                runs = (
                    [run["text"] for i, run in enumerate(flex_item2["text"]["runs"]) if i % 2 == 0]
                    if flex_item2
                    else []
                )
                if len(runs) > 1:
                    search_result["artist"] = runs[1]
                if len(runs) > 2:  # date may be missing
                    search_result["releaseDate"] = runs[2]
                search_result["resultType"] = "album"

    if result_type in ["song", "video", "episode"]:
        search_result["videoId"] = nav(
            data, [*PLAY_BUTTON, "playNavigationEndpoint", "watchEndpoint", "videoId"], True
        )
        search_result["videoType"] = video_type

    if result_type in ["song", "video", "album"]:
        search_result["duration"] = None
        search_result["year"] = None
        flex_item = get_flex_column_item(data, 1)
        runs = flex_item["text"]["runs"]
        if flex_item2 := get_flex_column_item(data, 2):
            runs.extend([{"text": ""}, *flex_item2["text"]["runs"]])  # first item is a dummy separator
        # ignore the first run if it is a type specifier (like "Single" or "Album")
        runs_offset = (len(runs[0]) == 1 and runs[0]["text"].lower() in api_search_result_types) * 2
        song_info = parse_song_runs(runs[runs_offset:])
        search_result.update(song_info)

    if result_type in ["artist", "album", "playlist", "profile", "podcast"]:
        search_result["browseId"] = nav(data, NAVIGATION_BROWSE_ID, True)

    if result_type in ["song", "album"]:
        search_result["isExplicit"] = nav(data, BADGE_LABEL, True) is not None

    if result_type in ["episode"]:
        flex_item = get_flex_column_item(data, 1)
        runs = nav(flex_item, TEXT_RUNS)[default_offset:]
        has_date = int(len(runs) > 1)
        search_result["live"] = bool(nav(data, ["badges", 0, "liveBadgeRenderer"], True))
        if has_date:
            search_result["date"] = runs[0]["text"]

        search_result["podcast"] = parse_id_name(runs[has_date * 2])

    search_result["thumbnails"] = nav(data, THUMBNAILS, True)

    return search_result


def parse_search_results(
    results: JsonList,
    api_search_result_types: list[str],
    resultType: str | None = None,
    category: str | None = None,
) -> JsonList:
    return [
        parse_search_result(result[MRLIR], api_search_result_types, resultType, category)
        for result in results
    ]


def get_search_params(filter: str | None, scope: str | None, ignore_spelling: bool) -> str | None:
    """
    Get search params for search query string based on user input

    :param filter: The search filter
    :param scope: The search scope
    :param ignore_spelling: If spelling shall be ignored
    :return: search param string
    """
    filtered_param1 = "EgWKAQ"
    params = None
    if filter is None and scope is None and not ignore_spelling:
        return params

    if scope == "uploads":
        params = "agIYAw%3D%3D"

    if scope == "library":
        if filter:
            param1 = filtered_param1
            param2 = _get_param2(filter)
            param3 = "AWoKEAUQCRADEAoYBA%3D%3D"
        else:
            params = "agIYBA%3D%3D"

    if scope is None and filter:
        if filter == "playlists":
            params = "Eg-KAQwIABAAGAAgACgB"
            if not ignore_spelling:
                params += "MABqChAEEAMQCRAFEAo%3D"
            else:
                params += "MABCAggBagoQBBADEAkQBRAK"

        elif "playlists" in filter:
            param1 = "EgeKAQQoA"
            if filter == "featured_playlists":
                param2 = "Dg"
            else:  # community_playlists
                param2 = "EA"

            if not ignore_spelling:
                param3 = "BagwQDhAKEAMQBBAJEAU%3D"
            else:
                param3 = "BQgIIAWoMEA4QChADEAQQCRAF"

        else:
            param1 = filtered_param1
            param2 = _get_param2(filter)
            if not ignore_spelling:
                param3 = "AWoMEA4QChADEAQQCRAF"
            else:
                param3 = "AUICCAFqDBAOEAoQAxAEEAkQBQ%3D%3D"

    if not scope and not filter and ignore_spelling:
        params = "EhGKAQ4IARABGAEgASgAOAFAAUICCAE%3D"

    return params if params else param1 + param2 + param3


def _get_param2(filter: str) -> str:
    filter_params = {
        "songs": "II",
        "videos": "IQ",
        "albums": "IY",
        "artists": "Ig",
        "playlists": "Io",
        "profiles": "JY",
        "podcasts": "JQ",
        "episodes": "JI",
    }
    return filter_params[filter]


def parse_search_suggestions(results: JsonDict, detailed_runs: bool) -> list[str] | JsonList:
    if not results.get("contents", [{}])[0].get("searchSuggestionsSectionRenderer", {}).get("contents", []):
        return []

    raw_suggestions = results["contents"][0]["searchSuggestionsSectionRenderer"]["contents"]
    suggestions = []

    for index, raw_suggestion in enumerate(raw_suggestions):
        feedback_token = None
        if "historySuggestionRenderer" in raw_suggestion:
            suggestion_content = raw_suggestion["historySuggestionRenderer"]
            # Extract feedbackToken if present
            feedback_token = nav(
                suggestion_content, ["serviceEndpoint", "feedbackEndpoint", "feedbackToken"], True
            )
        else:
            suggestion_content = raw_suggestion["searchSuggestionRenderer"]

        text = suggestion_content["navigationEndpoint"]["searchEndpoint"]["query"]
        runs = suggestion_content["suggestion"]["runs"]

        if detailed_runs:
            suggestions.append(
                {
                    "text": text,
                    "runs": runs,
                    "fromHistory": feedback_token is not None,
                    "feedbackToken": feedback_token,
                }
            )
        else:
            suggestions.append(text)

    return suggestions
