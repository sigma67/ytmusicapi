import re
from collections.abc import Callable

from ytmusicapi.type_alias import JsonDict, JsonList

from ._utils import *
from .constants import DOT_SEPARATOR_RUN


def parse_song_artists(data: JsonDict, index: int) -> JsonList:
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return []
    else:
        runs = flex_item["text"]["runs"]
        return parse_song_artists_runs(runs)


def parse_song_artists_runs(runs: JsonList) -> JsonList:
    artists = []
    for j in range(int(len(runs) / 2) + 1):
        artists.append({"name": runs[j * 2]["text"], "id": nav(runs[j * 2], NAVIGATION_BROWSE_ID, True)})
    return artists


def parse_song_run(run: JsonDict) -> JsonDict:
    text = run["text"]

    if "navigationEndpoint" in run:  # artist or album
        item = {"name": text, "id": nav(run, NAVIGATION_BROWSE_ID, True)}

        if item["id"] and (item["id"].startswith("MPRE") or "release_detail" in item["id"]):  # album
            return {"type": "album", "data": item}
        else:  # artist
            return {"type": "artist", "data": item}
    else:
        # note: YT uses non-breaking space \xa0 to separate number and magnitude
        if re.match(r"^\d([^ ])* [^ ]*$", text):
            return {"type": "views", "data": text.split(" ")[0]}

        elif re.match(r"^(\d+:)*\d+:\d+$", text):
            return {"type": "duration", "data": text}

        elif re.match(r"^\d{4}$", text):
            return {"type": "year", "data": text}

        else:  # artist without id
            return {"type": "artist", "data": {"name": text, "id": None}}


def parse_song_runs(runs: JsonList, skip_type_spec: bool = False) -> JsonDict:
    """
    :param skip_type_spec: if true, skip the type specifier (like "Song", "Single", or "Album") that may appear before artists ("Song • Eminem"). Otherwise, that text item is parsed as an artist with no ID.
    """

    parsed: JsonDict = {}

    # prevent type specifier from being parsed as an artist
    # it's the first run, separated from the actual artists by " • "
    if (
        skip_type_spec
        and len(runs) > 2
        and parse_song_run(runs[0])["type"] == "artist"
        and runs[1] == DOT_SEPARATOR_RUN
        and parse_song_run(runs[2])["type"] == "artist"
    ):
        runs = runs[2:]

    for i, run in list(enumerate(runs)):
        if i % 2:  # uneven items are always separators
            continue

        parsed_run = parse_song_run(run)
        data = parsed_run["data"]
        match parsed_run["type"]:
            case "album":
                parsed["album"] = data
            case "artist":
                parsed["artists"] = parsed.get("artists", [])
                parsed["artists"].append(data)
            case "views":
                parsed["views"] = data
            case "duration":
                parsed["duration"] = data
                parsed["duration_seconds"] = parse_duration(data)
            case "year":
                parsed["year"] = data

    return parsed


def parse_song_album(data: JsonDict, index: int) -> JsonDict | None:
    flex_item = get_flex_column_item(data, index)
    browse_id = nav(flex_item, TEXT_RUN + NAVIGATION_BROWSE_ID, True)
    return None if not flex_item else {"name": get_item_text(data, index), "id": browse_id}


def parse_song_menu_data(data: JsonDict) -> JsonDict:
    """
    :return: Dictionary with data from the provided song's context menu.

    Example::

        {
            "inLibrary": true,
            "feedbackTokens": {
                "add": "...",
                "remove": "..."
            },
            "pinnedToListenAgain": true,
            "listenAgainFeedbackTokens": {
                "pin": "...",
                "unpin": "..."
            }
        }
    """

    if "menu" not in data:
        return {}

    song_data: JsonDict = {}
    for item in nav(data, MENU_ITEMS):
        menu_item = nav(item, [TOGGLE_MENU], True) or nav(item, ["menuServiceItemRenderer"], True)
        if menu_item is None:
            continue

        song_data["inLibrary"] = song_data.get("inLibrary", False)
        song_data["pinnedToListenAgain"] = song_data.get("pinnedToListenAgain", False)

        current_icon_type = nav(menu_item, ["defaultIcon", "iconType"], True) or nav(
            menu_item, ["icon", "iconType"], True
        )
        feedback_token: Callable[[str], str | None] = lambda endpoint_type: nav(
            menu_item, [endpoint_type, *FEEDBACK_TOKEN], True
        )

        match current_icon_type:
            case "KEEP":
                song_data["listenAgainFeedbackTokens"] = {
                    "pin": feedback_token("defaultServiceEndpoint"),
                    "unpin": feedback_token("toggledServiceEndpoint"),
                }
            case "KEEP_OFF":
                song_data["pinnedToListenAgain"] = True
                song_data["listenAgainFeedbackTokens"] = {
                    "pin": feedback_token("toggledServiceEndpoint"),
                    "unpin": feedback_token("defaultServiceEndpoint"),
                }
            case "LIBRARY_ADD":
                song_data["feedbackTokens"] = {
                    "add": feedback_token("defaultServiceEndpoint"),
                    "remove": feedback_token("toggledServiceEndpoint"),
                }
            case "LIBRARY_SAVED":
                song_data["inLibrary"] = True
                song_data["feedbackTokens"] = {
                    "add": feedback_token("toggledServiceEndpoint"),
                    "remove": feedback_token("defaultServiceEndpoint"),
                }
            case "REMOVE_FROM_HISTORY":
                song_data["feedbackToken"] = feedback_token("serviceEndpoint")

    return song_data


def parse_like_status(service: JsonDict) -> str:
    status = ["LIKE", "INDIFFERENT"]
    return status[status.index(service["likeEndpoint"]["status"]) - 1]
