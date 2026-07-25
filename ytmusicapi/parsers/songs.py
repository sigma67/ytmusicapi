import re

from ytmusicapi.type_alias import JsonDict, JsonList

from ._utils import *
from .artists import parse_artists_runs
from .constants import DOT_SEPARATOR_RUN


def parse_song_artists(data: JsonDict, index: int) -> JsonList:
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return []
    else:
        runs = flex_item["text"]["runs"]
        return parse_artists_runs(runs)


# leading views word ("조회수 17억회", "播放次數：4505") or bidi mark (ur), up to the first digit  # noqa: RUF003
VIEWS_PREFIX = re.compile(r"^\D*?[\s:\uff1a\u200e-\u200f\u202a-\u202e]")


def parse_views(text: str) -> str | None:
    # only for non-latin scripts: "Maroon 5" is indistinguishable from a prefixed count
    prefixed = 0
    if not re.search(r"[a-zA-Z]", text):
        text, prefixed = VIEWS_PREFIX.subn("", text)

    if not re.match(r"^\d", text):
        return None

    # a bare ASCII token like "2Pac" is an artist, not a view count with a stripped word
    if not prefixed and text.isascii() and " " not in text:
        return None

    # note: \xa0 glues number and magnitude ("1,7\xa0Mrd. Aufrufe"), but some locales use
    # it before the views word too ("88\xa0k\xa0vues"); CJK has no separator ("3406万回視聴")
    head = text.split(" ")[0].split("\xa0")
    return "\xa0".join(head[:2])


def parse_song_run(run: JsonDict) -> JsonDict:
    text = run["text"]

    if "navigationEndpoint" in run:  # artist or album
        item = {"name": text, "id": nav(run, NAVIGATION_BROWSE_ID, True)}

        if item["id"] and (item["id"].startswith("MPRE") or "release_detail" in item["id"]):  # album
            return {"type": "album", "data": item}
        else:  # artist
            return {"type": "artist", "data": item}
    else:
        if re.match(r"^(\d+:)*\d+:\d+$", text):
            return {"type": "duration", "data": text}

        elif re.match(r"^\d{4}$", text):
            return {"type": "year", "data": text}

        elif (views := parse_views(text)) is not None:
            return {"type": "views", "data": views}

        else:  # artist without id
            return {"type": "artist", "data": {"name": text, "id": None}}


def parse_song_runs(runs: JsonList, skip_type_spec: bool = False) -> JsonDict:
    """
    :param skip_type_spec: if true, skip the type specifier (like "Song", "Single", or "Album") that may appear before artists ("Song • Eminem"). Otherwise, that text item is parsed as an artist with no ID.
    """

    parsed: JsonDict = {}

    # prevent type specifier from being parsed as an artist
    # it's the unlinked first run, separated by " • " from the artists, or from
    # metadata (duration/views/year) when the song lists no artist at all
    if (
        skip_type_spec
        and len(runs) > 2
        and "navigationEndpoint" not in runs[0]
        and parse_song_run(runs[0])["type"] == "artist"
        and runs[1] == DOT_SEPARATOR_RUN
        and parse_song_run(runs[2])["type"] in ("artist", "duration", "views", "year")
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

        def feedback_token(endpoint_type: str, menu_item: JsonDict = menu_item) -> str | None:
            return nav(menu_item, [endpoint_type, *FEEDBACK_TOKEN], True)

        # YTM signals the current state with isToggled instead of swapping the default/toggled icons
        is_toggled = bool(menu_item.get("isToggled"))

        match current_icon_type:
            case "KEEP":  # pin to listen again
                song_data["pinnedToListenAgain"] = is_toggled
                song_data["listenAgainFeedbackTokens"] = {
                    "pin": feedback_token("defaultServiceEndpoint"),
                    "unpin": feedback_token("toggledServiceEndpoint"),
                }
            case "KEEP_OFF":  # unpin from listen again
                song_data["pinnedToListenAgain"] = True
                song_data["listenAgainFeedbackTokens"] = {
                    "pin": feedback_token("toggledServiceEndpoint"),
                    "unpin": feedback_token("defaultServiceEndpoint"),
                }
            case "BOOKMARK_BORDER":  # add to library
                song_data["inLibrary"] = is_toggled
                song_data["feedbackTokens"] = {
                    "add": feedback_token("defaultServiceEndpoint"),
                    "remove": feedback_token("toggledServiceEndpoint"),
                }
            case "BOOKMARK":  # remove from library
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
