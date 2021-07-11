# commonly used navigation paths
RUN_TEXT = ['runs', 0, 'text']
TAB_CONTENT = ['tabs', 0, 'tabRenderer', 'content']
SINGLE_COLUMN_TAB = ['contents', 'singleColumnBrowseResultsRenderer'] + TAB_CONTENT
SECTION_LIST = ['sectionListRenderer', 'contents']
SECTION_LIST_ITEM = ['sectionListRenderer', 'contents', 0]
ITEM_SECTION = ['itemSectionRenderer', 'contents', 0]
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
NAVIGATION_BROWSE_ID = ['navigationEndpoint', 'browseEndpoint', 'browseId']
NAVIGATION_VIDEO_ID = ['navigationEndpoint', 'watchEndpoint', 'videoId']
NAVIGATION_PLAYLIST_ID = ['navigationEndpoint', 'watchEndpoint', 'playlistId']
NAVIGATION_WATCH_PLAYLIST_ID = ['navigationEndpoint', 'watchPlaylistEndpoint', 'playlistId']
HEADER_DETAIL = ['header', 'musicDetailHeaderRenderer']
DESCRIPTION = ['description'] + RUN_TEXT
CAROUSEL = ['musicCarouselShelfRenderer']
CAROUSEL_CONTENTS = CAROUSEL + ['contents']
CAROUSEL_TITLE = ['header', 'musicCarouselShelfBasicHeaderRenderer', 'title', 'runs', 0]
FRAMEWORK_MUTATIONS = ['frameworkUpdates', 'entityBatchUpdate', 'mutations']
TITLE = ['title', 'runs', 0]
TITLE_TEXT = ['title'] + RUN_TEXT
TEXT_RUN = ['text', 'runs', 0]
TEXT_RUN_TEXT = ['text', 'runs', 0, 'text']
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
RELOAD_CONTINUATION = ['continuations', 0, 'reloadContinuationData', 'continuation']
CATEGORY_TITLE = ['musicNavigationButtonRenderer', 'buttonText'] + RUN_TEXT
CATEGORY_PARAMS = ['musicNavigationButtonRenderer', 'clickCommand', 'browseEndpoint', 'params']
MRLIR = 'musicResponsiveListItemRenderer'
MTRIR = 'musicTwoRowItemRenderer'