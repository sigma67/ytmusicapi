"""commonly used navigation paths"""

from typing import Any, Literal, overload

from ytmusicapi.type_alias import JsonDict, JsonList

CONTENT = ["contents", 0]
RUN_TEXT = ["runs", 0, "text"]
TAB_CONTENT = ["tabs", 0, "tabRenderer", "content"]
TAB_1_CONTENT = ["tabs", 1, "tabRenderer", "content"]
TAB_2_CONTENT = ["tabs", 2, "tabRenderer", "content"]
TWO_COLUMN_RENDERER = ["contents", "twoColumnBrowseResultsRenderer"]
SINGLE_COLUMN = ["contents", "singleColumnBrowseResultsRenderer"]
SINGLE_COLUMN_TAB = SINGLE_COLUMN + TAB_CONTENT
SECTION = ["sectionListRenderer"]
SECTION_LIST = [*SECTION, "contents"]
SECTION_LIST_ITEM = SECTION + CONTENT
RESPONSIVE_HEADER = ["musicResponsiveHeaderRenderer"]
ITEM_SECTION = ["itemSectionRenderer", *CONTENT]
MUSIC_SHELF = ["musicShelfRenderer"]
GRID = ["gridRenderer"]
GRID_ITEMS = [*GRID, "items"]
MENU = ["menu", "menuRenderer"]
MENU_ITEMS = [*MENU, "items"]
MENU_LIKE_STATUS = [*MENU, "topLevelButtons", 0, "likeButtonRenderer", "likeStatus"]
MENU_SERVICE = ["menuServiceItemRenderer", "serviceEndpoint"]
TOGGLE_MENU = "toggleMenuServiceItemRenderer"
OVERLAY_RENDERER = ["musicItemThumbnailOverlayRenderer", "content", "musicPlayButtonRenderer"]
PLAY_BUTTON = ["overlay", *OVERLAY_RENDERER]
NAVIGATION_BROWSE = ["navigationEndpoint", "browseEndpoint"]
NAVIGATION_BROWSE_ID = [*NAVIGATION_BROWSE, "browseId"]
PAGE_TYPE = ["browseEndpointContextSupportedConfigs", "browseEndpointContextMusicConfig", "pageType"]
WATCH_VIDEO_ID = ["watchEndpoint", "videoId"]
PLAYLIST_ID = ["playlistId"]
WATCH_PLAYLIST_ID = ["watchEndpoint", *PLAYLIST_ID]
NAVIGATION_VIDEO_ID = ["navigationEndpoint", *WATCH_VIDEO_ID]
QUEUE_VIDEO_ID = ["queueAddEndpoint", "queueTarget", "videoId"]
NAVIGATION_PLAYLIST_ID = ["navigationEndpoint", *WATCH_PLAYLIST_ID]
WATCH_PID = ["watchPlaylistEndpoint", *PLAYLIST_ID]
NAVIGATION_WATCH_PLAYLIST_ID = ["navigationEndpoint", *WATCH_PID]
NAVIGATION_VIDEO_TYPE = [
    "watchEndpoint",
    "watchEndpointMusicSupportedConfigs",
    "watchEndpointMusicConfig",
    "musicVideoType",
]
ICON_TYPE = ["icon", "iconType"]
TOGGLED_BUTTON = ["toggleButtonRenderer", "isToggled"]
TITLE = ["title", "runs", 0]
TITLE_TEXT = ["title", *RUN_TEXT]
TEXT_RUNS = ["text", "runs"]
TEXT_RUN = [*TEXT_RUNS, 0]
TEXT_RUN_TEXT = [*TEXT_RUN, "text"]
SUBTITLE = ["subtitle", *RUN_TEXT]
SUBTITLE_RUNS = ["subtitle", "runs"]
SUBTITLE_RUN = [*SUBTITLE_RUNS, 0]
SUBTITLE2 = [*SUBTITLE_RUNS, 2, "text"]
SUBTITLE3 = [*SUBTITLE_RUNS, 4, "text"]
THUMBNAIL = ["thumbnail", "thumbnails"]
THUMBNAILS = ["thumbnail", "musicThumbnailRenderer", *THUMBNAIL]
THUMBNAIL_RENDERER = ["thumbnailRenderer", "musicThumbnailRenderer", *THUMBNAIL]
THUMBNAIL_OVERLAY_NAVIGATION = ["thumbnailOverlay", *OVERLAY_RENDERER, "playNavigationEndpoint"]
THUMBNAIL_OVERLAY = [*THUMBNAIL_OVERLAY_NAVIGATION, *WATCH_PID]
THUMBNAIL_CROPPED = ["thumbnail", "croppedSquareThumbnailRenderer", *THUMBNAIL]
FEEDBACK_TOKEN = ["feedbackEndpoint", "feedbackToken"]
BADGE_PATH = [0, "musicInlineBadgeRenderer", "accessibilityData", "accessibilityData", "label"]
BADGE_LABEL = ["badges", *BADGE_PATH]
SUBTITLE_BADGE_LABEL = ["subtitleBadges", *BADGE_PATH]
CATEGORY_TITLE = ["musicNavigationButtonRenderer", "buttonText", *RUN_TEXT]
CATEGORY_PARAMS = ["musicNavigationButtonRenderer", "clickCommand", "browseEndpoint", "params"]
MMRIR = "musicMultiRowListItemRenderer"
MRLIR = "musicResponsiveListItemRenderer"
MTRIR = "musicTwoRowItemRenderer"
MNIR = "menuNavigationItemRenderer"
TASTE_PROFILE_ITEMS = ["contents", "tastebuilderRenderer", "contents"]
TASTE_PROFILE_ARTIST = ["title", "runs"]
SECTION_LIST_CONTINUATION = ["continuationContents", "sectionListContinuation"]
MENU_PLAYLIST_ID = [*MENU_ITEMS, 0, MNIR, *NAVIGATION_WATCH_PLAYLIST_ID]
MULTI_SELECT = ["musicMultiSelectMenuItemRenderer"]
HEADER = ["header"]
HEADER_DETAIL = [*HEADER, "musicDetailHeaderRenderer"]
EDITABLE_PLAYLIST_DETAIL_HEADER = ["musicEditablePlaylistDetailHeaderRenderer"]
HEADER_EDITABLE_DETAIL = [*HEADER, *EDITABLE_PLAYLIST_DETAIL_HEADER]
HEADER_SIDE = [*HEADER, "musicSideAlignedItemRenderer"]
HEADER_MUSIC_VISUAL = [*HEADER, "musicVisualHeaderRenderer"]
DESCRIPTION_SHELF = ["musicDescriptionShelfRenderer"]
DESCRIPTION = ["description", *RUN_TEXT]
CAROUSEL = ["musicCarouselShelfRenderer"]
IMMERSIVE_CAROUSEL = ["musicImmersiveCarouselShelfRenderer"]
CAROUSEL_CONTENTS = [*CAROUSEL, "contents"]
CAROUSEL_TITLE = [*HEADER, "musicCarouselShelfBasicHeaderRenderer", *TITLE]
CARD_SHELF_TITLE = [*HEADER, "musicCardShelfHeaderBasicRenderer", *TITLE_TEXT]
FRAMEWORK_MUTATIONS = ["frameworkUpdates", "entityBatchUpdate", "mutations"]
TIMESTAMPED_LYRICS = [
    "contents",
    "elementRenderer",
    "newElement",
    "type",
    "componentType",
    "model",
    "timedLyricsModel",
    "lyricsData",
]


@overload
def nav(root: JsonDict | None, items: list[Any], none_if_absent: Literal[False] = False) -> Any:
    """overload for mypy only"""


@overload
def nav(root: JsonDict | None, items: list[Any], none_if_absent: Literal[True] = True) -> Any | None:
    """overload for mypy only"""


def nav(root: JsonDict | None, items: list[Any], none_if_absent: bool = False) -> Any | None:
    """Access a nested object in root by item sequence."""
    if root is None:
        return None
    try:
        for k in items:
            root = root[k]  # type: ignore[index]
    except (KeyError, IndexError) as e:
        if none_if_absent:
            return None
        raise type(e)(f"Unable to find '{k}' using path {items!r} on {root!r}, exception: {e}")
    return root


def find_object_by_key(
    object_list: JsonList, key: str, nested: str | None = None, is_key: bool = False
) -> JsonDict | None:
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            return item[key] if is_key else item

    return None


def find_objects_by_key(object_list: JsonList, key: str, nested: str | None = None) -> JsonList:
    objects = []
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            objects.append(item)
    return objects
