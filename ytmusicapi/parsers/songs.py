import re

from ytmusicapi.type_alias import JsonDict, JsonList

from ._utils import *
from .constants import DOT_SEPARATOR_RUN


def parse_song_artists(data: JsonDict, index: int) -> JsonList:
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return []
    else:
        runs = flex_item["text"]["runs"]
        return parse_artists_runs(runs)


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


def parse_song_library_status(item: JsonDict) -> bool:
    """Returns True if song is in the library"""
    library_status = nav(item, [TOGGLE_MENU, "defaultIcon", "iconType"], True)

    return library_status == "LIBRARY_SAVED"


def parse_song_menu_tokens(item: JsonDict) -> dict[str, str | None]:
    toggle_menu = item[TOGGLE_MENU]

    library_add_token = nav(toggle_menu, ["defaultServiceEndpoint", *FEEDBACK_TOKEN], True)
    library_remove_token = nav(toggle_menu, ["toggledServiceEndpoint", *FEEDBACK_TOKEN], True)

    in_library = parse_song_library_status(item)
    if in_library:
        library_add_token, library_remove_token = library_remove_token, library_add_token

    return {"add": library_add_token, "remove": library_remove_token}


def parse_like_status(service: JsonDict) -> str:
    status = ["LIKE", "INDIFFERENT"]
    return status[status.index(service["likeEndpoint"]["status"]) - 1]
