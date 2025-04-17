import typing
from collections.abc import Callable
from functools import wraps
from gettext import GNUTranslations
from typing import ParamSpec, TypeVar

from ytmusicapi.navigation import *
from ytmusicapi.type_alias import JsonDict, JsonList

P = ParamSpec("P")
R = TypeVar("R")

if typing.TYPE_CHECKING:
    pass


def parse_menu_playlists(data: JsonDict, result: JsonDict) -> None:
    """performs in-place replacement based on :param:data: in :param:result"""
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


def get_item_text(item: JsonDict, index: int, run_index: int = 0, none_if_absent: bool = False) -> str | None:
    column = get_flex_column_item(item, index)
    if not column:
        return None
    if none_if_absent and len(column["text"]["runs"]) < run_index + 1:
        return None

    return typing.cast(str, column["text"]["runs"][run_index]["text"])


def get_flex_column_item(item: JsonDict, index: int) -> JsonDict | None:
    if (
        len(item["flexColumns"]) <= index
        or "text" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]
        or "runs" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]["text"]
    ):
        return None

    return typing.cast(JsonDict, item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"])


def get_fixed_column_item(item: JsonDict, index: int) -> JsonDict | None:
    if (
        "text" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]
        or "runs" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]["text"]
    ):
        return None

    return typing.cast(JsonDict, item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"])


def get_dot_separator_index(runs: JsonList) -> int:
    try:
        index = runs.index({"text": " • "})
    except ValueError:
        index = len(runs)

    return index


def parse_duration(duration: str | None) -> int | None:
    """
    Parse duration to a value in seconds.

    :param duration: Duration string
    :return: Duration in seconds
    """
    # duration may be falsy or a single space: ' '
    if not duration or not duration.strip():
        return None
    duration_split = duration.strip().split(":")
    for d in duration_split:
        if not d.isdigit():  # For e.g: "2,343"
            return None
    mapped_increments = zip([1, 60, 3600], reversed(duration_split))
    seconds = sum(multiplier * int(time) for multiplier, time in mapped_increments)
    return seconds


class SupportsLang(typing.Protocol):
    lang: GNUTranslations


def i18n(method: Callable[P, R]) -> Callable[P, R]:
    @wraps(method)
    def _impl(*args: P.args, **kwargs: P.kwargs) -> R:
        self = args[0]
        method.__globals__["_"] = self.lang.gettext  # type: ignore
        return method(*args, **kwargs)

    return _impl


def parse_id_name(sub_run: JsonDict | None) -> JsonDict:
    return {
        "id": nav(sub_run, NAVIGATION_BROWSE_ID, True),
        "name": nav(sub_run, ["text"], True),
    }
