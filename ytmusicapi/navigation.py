# commonly used navigation paths
CONTENT = ["contents", 0]
RUN_TEXT = ["runs", 0, "text"]
TAB_CONTENT = ["tabs", 0, "tabRenderer", "content"]
TAB_1_CONTENT = ["tabs", 1, "tabRenderer", "content"]
SINGLE_COLUMN = ["contents", "singleColumnBrowseResultsRenderer"]
SINGLE_COLUMN_TAB = SINGLE_COLUMN + TAB_CONTENT
SECTION_LIST = ["sectionListRenderer", "contents"]
SECTION_LIST_ITEM = ["sectionListRenderer"] + CONTENT
ITEM_SECTION = ["itemSectionRenderer"] + CONTENT
MUSIC_SHELF = ["musicShelfRenderer"]
GRID = ["gridRenderer"]
GRID_ITEMS = GRID + ["items"]
MENU = ["menu", "menuRenderer"]
MENU_ITEMS = MENU + ["items"]
MENU_LIKE_STATUS = MENU + ["topLevelButtons", 0, "likeButtonRenderer", "likeStatus"]
MENU_SERVICE = ["menuServiceItemRenderer", "serviceEndpoint"]
TOGGLE_MENU = "toggleMenuServiceItemRenderer"
PLAY_BUTTON = ["overlay", "musicItemThumbnailOverlayRenderer", "content", "musicPlayButtonRenderer"]
NAVIGATION_BROWSE = ["navigationEndpoint", "browseEndpoint"]
NAVIGATION_BROWSE_ID = NAVIGATION_BROWSE + ["browseId"]
PAGE_TYPE = ["browseEndpointContextSupportedConfigs", "browseEndpointContextMusicConfig", "pageType"]
WATCH_VIDEO_ID = ["watchEndpoint", "videoId"]
NAVIGATION_VIDEO_ID = ["navigationEndpoint"] + WATCH_VIDEO_ID
QUEUE_VIDEO_ID = ["queueAddEndpoint", "queueTarget", "videoId"]
NAVIGATION_PLAYLIST_ID = ["navigationEndpoint", "watchEndpoint", "playlistId"]
NAVIGATION_WATCH_PLAYLIST_ID = ["navigationEndpoint", "watchPlaylistEndpoint", "playlistId"]
NAVIGATION_VIDEO_TYPE = [
    "watchEndpoint",
    "watchEndpointMusicSupportedConfigs",
    "watchEndpointMusicConfig",
    "musicVideoType",
]
TITLE = ["title", "runs", 0]
TITLE_TEXT = ["title"] + RUN_TEXT
TEXT_RUNS = ["text", "runs"]
TEXT_RUN = TEXT_RUNS + [0]
TEXT_RUN_TEXT = TEXT_RUN + ["text"]
SUBTITLE = ["subtitle"] + RUN_TEXT
SUBTITLE_RUNS = ["subtitle", "runs"]
SUBTITLE2 = SUBTITLE_RUNS + [2, "text"]
SUBTITLE3 = SUBTITLE_RUNS + [4, "text"]
THUMBNAIL = ["thumbnail", "thumbnails"]
THUMBNAILS = ["thumbnail", "musicThumbnailRenderer"] + THUMBNAIL
THUMBNAIL_RENDERER = ["thumbnailRenderer", "musicThumbnailRenderer"] + THUMBNAIL
THUMBNAIL_CROPPED = ["thumbnail", "croppedSquareThumbnailRenderer"] + THUMBNAIL
FEEDBACK_TOKEN = ["feedbackEndpoint", "feedbackToken"]
BADGE_PATH = [0, "musicInlineBadgeRenderer", "accessibilityData", "accessibilityData", "label"]
BADGE_LABEL = ["badges"] + BADGE_PATH
SUBTITLE_BADGE_LABEL = ["subtitleBadges"] + BADGE_PATH
CATEGORY_TITLE = ["musicNavigationButtonRenderer", "buttonText"] + RUN_TEXT
CATEGORY_PARAMS = ["musicNavigationButtonRenderer", "clickCommand", "browseEndpoint", "params"]
MRLIR = "musicResponsiveListItemRenderer"
MTRIR = "musicTwoRowItemRenderer"
TASTE_PROFILE_ITEMS = ["contents", "tastebuilderRenderer", "contents"]
TASTE_PROFILE_ARTIST = ["title", "runs"]
SECTION_LIST_CONTINUATION = ["continuationContents", "sectionListContinuation"]
MENU_PLAYLIST_ID = MENU_ITEMS + [0, "menuNavigationItemRenderer"] + NAVIGATION_WATCH_PLAYLIST_ID
HEADER_DETAIL = ["header", "musicDetailHeaderRenderer"]
DESCRIPTION_SHELF = ["musicDescriptionShelfRenderer"]
DESCRIPTION = ["description"] + RUN_TEXT
CAROUSEL = ["musicCarouselShelfRenderer"]
IMMERSIVE_CAROUSEL = ["musicImmersiveCarouselShelfRenderer"]
CAROUSEL_CONTENTS = CAROUSEL + ["contents"]
CAROUSEL_TITLE = ["header", "musicCarouselShelfBasicHeaderRenderer"] + TITLE
CARD_SHELF_TITLE = ["header", "musicCardShelfHeaderBasicRenderer"] + TITLE_TEXT
FRAMEWORK_MUTATIONS = ["frameworkUpdates", "entityBatchUpdate", "mutations"]


def nav(root, items, none_if_absent=False):
    """Access a nested object in root by item sequence."""
    try:
        for k in items:
            root = root[k]
        return root
    except Exception as err:
        if none_if_absent:
            return None
        else:
            raise err


def find_object_by_key(object_list, key, nested=None, is_key=False):
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            return item[key] if is_key else item
    return None


def find_objects_by_key(object_list, key, nested=None):
    objects = []
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            objects.append(item)
    return objects
