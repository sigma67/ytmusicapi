from ._utils import *
from .songs import *


def get_search_result_type(result_type_local, result_types_local):
    if not result_type_local:
        return None
    result_types = ["artist", "playlist", "song", "video", "station", "profile", "podcast", "episode"]
    result_type_local = result_type_local.lower()
    # default to album since it's labeled with multiple values ('Single', 'EP', etc.)
    if result_type_local not in result_types_local:
        result_type = "album"
    else:
        result_type = result_types[result_types_local.index(result_type_local)]

    return result_type


def parse_top_result(data, search_result_types):
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
        song_info = parse_song_runs(runs)
        search_result.update(song_info)

    if result_type in ["album"]:
        search_result["browseId"] = nav(data, TITLE + NAVIGATION_BROWSE_ID, True)

    if result_type in ["playlist"]:
        search_result["playlistId"] = nav(data, MENU_PLAYLIST_ID)
        search_result["title"] = nav(data, TITLE_TEXT)
        search_result["author"] = parse_song_artists_runs(nav(data, ["subtitle", "runs"])[2:])

    search_result["thumbnails"] = nav(data, THUMBNAILS, True)
    return search_result


def parse_search_result(data, search_result_types, result_type, category):
    default_offset = (not result_type or result_type == "album") * 2
    search_result = {"category": category}
    video_type = nav(data, [*PLAY_BUTTON, "playNavigationEndpoint", *NAVIGATION_VIDEO_TYPE], True)
    if not result_type and video_type:
        result_type = "song" if video_type == "MUSIC_VIDEO_TYPE_ATV" else "video"

    result_type = (
        get_search_result_type(get_item_text(data, 1), search_result_types)
        if not result_type
        else result_type
    )
    search_result["resultType"] = result_type

    if result_type != "artist":
        search_result["title"] = get_item_text(data, 0)

    if result_type == "artist":
        search_result["artist"] = get_item_text(data, 0)
        parse_menu_playlists(data, search_result)

    elif result_type == "album":
        search_result["type"] = get_item_text(data, 1)

    elif result_type == "playlist":
        flex_item = get_flex_column_item(data, 1)["text"]["runs"]
        has_author = len(flex_item) == default_offset + 3
        search_result["itemCount"] = get_item_text(data, 1, default_offset + has_author * 2).split(" ")[0]
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
                runs = [run["text"] for i, run in enumerate(flex_item2["text"]["runs"]) if i % 2 == 0]
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
        song_info = parse_song_runs(runs)
        search_result.update(song_info)

    if result_type in ["artist", "album", "playlist", "profile", "podcast"]:
        search_result["browseId"] = nav(data, NAVIGATION_BROWSE_ID, True)

    if result_type in ["song", "album"]:
        search_result["isExplicit"] = nav(data, BADGE_LABEL, True) is not None

    if result_type in ["episode"]:
        flex_item = get_flex_column_item(data, 1)
        has_date = int(len(nav(flex_item, TEXT_RUNS)) > 1)
        search_result["live"] = bool(nav(data, ["badges", 0, "liveBadgeRenderer"], True))
        if has_date:
            search_result["date"] = nav(flex_item, TEXT_RUN_TEXT)

        search_result["podcast"] = parse_id_name(nav(flex_item, ["text", "runs", has_date * 2]))

    search_result["thumbnails"] = nav(data, THUMBNAILS, True)

    return search_result


def parse_search_results(results, search_result_types, resultType=None, category=None):
    return [
        parse_search_result(result[MRLIR], search_result_types, resultType, category) for result in results
    ]


def get_search_params(filter, scope, ignore_spelling):
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


def _get_param2(filter):
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


def parse_search_suggestions(results, detailed_runs):
    if not results.get("contents", [{}])[0].get("searchSuggestionsSectionRenderer", {}).get("contents", []):
        return []

    raw_suggestions = results["contents"][0]["searchSuggestionsSectionRenderer"]["contents"]
    suggestions = []

    for raw_suggestion in raw_suggestions:
        if "historySuggestionRenderer" in raw_suggestion:
            suggestion_content = raw_suggestion["historySuggestionRenderer"]
            from_history = True
        else:
            suggestion_content = raw_suggestion["searchSuggestionRenderer"]
            from_history = False

        text = suggestion_content["navigationEndpoint"]["searchEndpoint"]["query"]
        runs = suggestion_content["suggestion"]["runs"]

        if detailed_runs:
            suggestions.append({"text": text, "runs": runs, "fromHistory": from_history})
        else:
            suggestions.append(text)

    return suggestions
