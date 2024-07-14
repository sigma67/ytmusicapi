from functools import wraps

from ytmusicapi.navigation import *


def parse_menu_playlists(data, result):
    menu_items = nav(data, MENU_ITEMS, True)
    if menu_items is None:
        return
    watch_menu = find_objects_by_key(menu_items, MNIR)
    for item in [_x[MNIR] for _x in watch_menu]:
        icon = nav(item, ICON_TYPE)
        if icon == "MUSIC_SHUFFLE":
            watch_key = "shuffleId"
        elif icon == "MIX":
            watch_key = "radioId"
        else:
            continue

        watch_id = nav(item, ["navigationEndpoint", "watchPlaylistEndpoint", "playlistId"], True)
        if not watch_id:
            watch_id = nav(item, ["navigationEndpoint", "watchEndpoint", "playlistId"], True)
        if watch_id:
            result[watch_key] = watch_id


def get_item_text(item, index, run_index=0, none_if_absent=False):
    column = get_flex_column_item(item, index)
    if not column:
        return None
    if none_if_absent and len(column["text"]["runs"]) < run_index + 1:
        return None
    return column["text"]["runs"][run_index]["text"]


def get_flex_column_item(item, index):
    if (
        len(item["flexColumns"]) <= index
        or "text" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]
        or "runs" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]["text"]
    ):
        return None

    return item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]


def get_fixed_column_item(item, index):
    if (
        "text" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]
        or "runs" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]["text"]
    ):
        return None

    return item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]


def get_dot_separator_index(runs):
    try:
        index = runs.index({"text": " • "})
    except ValueError:
        index = len(runs)

    return index


def parse_duration(duration):
    # duration may be falsy or a single space: ' '
    if not duration or not duration.strip():
        return duration
    mapped_increments = zip([1, 60, 3600], reversed(duration.split(":")))
    seconds = sum(multiplier * int(time) for multiplier, time in mapped_increments)
    return seconds


def i18n(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method.__globals__["_"] = self.lang.gettext
        return method(self, *method_args, **method_kwargs)

    return _impl


def parse_id_name(sub_run):
    return {
        "id": nav(sub_run, NAVIGATION_BROWSE_ID, True),
        "name": nav(sub_run, ["text"], True),
    }
