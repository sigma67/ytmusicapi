# commonly used navigation paths
CONTENT = ['contents', 0]
RUN_TEXT = ['runs', 0, 'text']
TAB_CONTENT = ['tabs', 0, 'tabRenderer', 'content']
SINGLE_COLUMN_TAB = ['contents', 'singleColumnBrowseResultsRenderer'] + TAB_CONTENT
SECTION_LIST = ['sectionListRenderer', 'contents']
SECTION_LIST_ITEM = ['sectionListRenderer'] + CONTENT
ITEM_SECTION = ['itemSectionRenderer'] + CONTENT
MUSIC_SHELF = ['musicShelfRenderer']
GRID = ['gridRenderer']
GRID_ITEMS = GRID + ['items']
MENU = ['menu', 'menuRenderer']
MENU_ITEMS = MENU + ['items']
MENU_LIKE_STATUS = MENU + ['topLevelButtons', 0, 'likeButtonRenderer', 'likeStatus']
MENU_SERVICE = ['menuServiceItemRenderer', 'serviceEndpoint']
TOGGLE_MENU = 'toggleMenuServiceItemRenderer'
PLAY_BUTTON = [
    'overlay', 'musicItemThumbnailOverlayRenderer', 'content', 'musicPlayButtonRenderer'
]
NAVIGATION_BROWSE = ['navigationEndpoint', 'browseEndpoint']
NAVIGATION_BROWSE_ID = NAVIGATION_BROWSE + ['browseId']
PAGE_TYPE = [
    'browseEndpointContextSupportedConfigs', 'browseEndpointContextMusicConfig', 'pageType'
]
NAVIGATION_VIDEO_ID = ['navigationEndpoint', 'watchEndpoint', 'videoId']
NAVIGATION_PLAYLIST_ID = ['navigationEndpoint', 'watchEndpoint', 'playlistId']
NAVIGATION_WATCH_PLAYLIST_ID = ['navigationEndpoint', 'watchPlaylistEndpoint', 'playlistId']
NAVIGATION_VIDEO_TYPE = [
    'watchEndpoint', 'watchEndpointMusicSupportedConfigs', 'watchEndpointMusicConfig',
    'musicVideoType'
]
HEADER_DETAIL = ['header', 'musicDetailHeaderRenderer']
DESCRIPTION_SHELF = ['musicDescriptionShelfRenderer']
DESCRIPTION = ['description'] + RUN_TEXT
CAROUSEL = ['musicCarouselShelfRenderer']
IMMERSIVE_CAROUSEL = ['musicImmersiveCarouselShelfRenderer']
CAROUSEL_CONTENTS = CAROUSEL + ['contents']
CAROUSEL_TITLE = ['header', 'musicCarouselShelfBasicHeaderRenderer', 'title', 'runs', 0]
FRAMEWORK_MUTATIONS = ['frameworkUpdates', 'entityBatchUpdate', 'mutations']
TITLE = ['title', 'runs', 0]
TITLE_TEXT = ['title'] + RUN_TEXT
TEXT_RUNS = ['text', 'runs']
TEXT_RUN = TEXT_RUNS + [0]
TEXT_RUN_TEXT = TEXT_RUN + ['text']
SUBTITLE = ['subtitle'] + RUN_TEXT
SUBTITLE2 = ['subtitle', 'runs', 2, 'text']
SUBTITLE3 = ['subtitle', 'runs', 4, 'text']
THUMBNAIL = ['thumbnail', 'thumbnails']
THUMBNAILS = ['thumbnail', 'musicThumbnailRenderer'] + THUMBNAIL
THUMBNAIL_RENDERER = ['thumbnailRenderer', 'musicThumbnailRenderer'] + THUMBNAIL
THUMBNAIL_CROPPED = ['thumbnail', 'croppedSquareThumbnailRenderer'] + THUMBNAIL
FEEDBACK_TOKEN = ['feedbackEndpoint', 'feedbackToken']
BADGE_LABEL = [
    'badges', 0, 'musicInlineBadgeRenderer', 'accessibilityData', 'accessibilityData', 'label'
]
CATEGORY_TITLE = ['musicNavigationButtonRenderer', 'buttonText'] + RUN_TEXT
CATEGORY_PARAMS = ['musicNavigationButtonRenderer', 'clickCommand', 'browseEndpoint', 'params']
MRLIR = 'musicResponsiveListItemRenderer'
MTRIR = 'musicTwoRowItemRenderer'
TASTE_PROFILE_ITEMS = ["contents", "tastebuilderRenderer", "contents"]
TASTE_PROFILE_ARTIST = ["title", "runs"]
SECTION_LIST_CONTINUATION = ['continuationContents', 'sectionListContinuation']


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
