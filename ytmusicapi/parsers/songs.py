import re

from ._utils import *


def parse_song_artists(data, index):
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return None
    else:
        runs = flex_item["text"]["runs"]
        return parse_song_artists_runs(runs)


def parse_song_artists_runs(runs):
    artists = []
    for j in range(int(len(runs) / 2) + 1):
        artists.append({"name": runs[j * 2]["text"], "id": nav(runs[j * 2], NAVIGATION_BROWSE_ID, True)})
    return artists


def parse_song_runs(runs):
    parsed = {"artists": []}
    for i, run in enumerate(runs):
        if i % 2:  # uneven items are always separators
            continue
        text = run["text"]
        if "navigationEndpoint" in run:  # artist or album
            item = {"name": text, "id": nav(run, NAVIGATION_BROWSE_ID, True)}

            if item["id"] and (item["id"].startswith("MPRE") or "release_detail" in item["id"]):  # album
                parsed["album"] = item
            else:  # artist
                parsed["artists"].append(item)

        else:
            # note: YT uses non-breaking space \xa0 to separate number and magnitude
            if re.match(r"^\d([^ ])* [^ ]*$", text) and i > 0:
                parsed["views"] = text.split(" ")[0]

            elif re.match(r"^(\d+:)*\d+:\d+$", text):
                parsed["duration"] = text
                parsed["duration_seconds"] = parse_duration(text)

            elif re.match(r"^\d{4}$", text):
                parsed["year"] = text

            else:  # artist without id
                parsed["artists"].append({"name": text, "id": None})

    return parsed


def parse_song_album(data, index):
    flex_item = get_flex_column_item(data, index)
    return None if not flex_item else {"name": get_item_text(data, index), "id": get_browse_id(flex_item, 0)}


def parse_song_library_status(item) -> bool:
    """Returns True if song is in the library"""
    library_status = nav(item, [TOGGLE_MENU, "defaultIcon", "iconType"], True)

    return library_status == "LIBRARY_SAVED"


def parse_song_menu_tokens(item):
    toggle_menu = item[TOGGLE_MENU]

    library_add_token = nav(toggle_menu, ["defaultServiceEndpoint"] + FEEDBACK_TOKEN, True)
    library_remove_token = nav(toggle_menu, ["toggledServiceEndpoint"] + FEEDBACK_TOKEN, True)

    in_library = parse_song_library_status(item)
    if in_library:
        library_add_token, library_remove_token = library_remove_token, library_add_token

    return {"add": library_add_token, "remove": library_remove_token}


def parse_like_status(service):
    status = ["LIKE", "INDIFFERENT"]
    return status[status.index(service["likeEndpoint"]["status"]) - 1]
