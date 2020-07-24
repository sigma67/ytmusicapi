# commonly used navigation paths
SINGLE_COLUMN_TAB = [
    'contents', 'singleColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content'
]
SECTION_LIST = ['sectionListRenderer', 'contents']
ITEM_SECTION = ['itemSectionRenderer', 'contents', 0]
MUSIC_SHELF = [0, 'musicShelfRenderer']
MENU = ['menu', 'menuRenderer']
MENU_ITEMS = MENU + ['items']
MENU_LIKE_STATUS = MENU + ['topLevelButtons', 0, 'likeButtonRenderer', 'likeStatus']
MENU_SERVICE = ['menuServiceItemRenderer', 'serviceEndpoint']
PLAY_BUTTON = [
    'overlay', 'musicItemThumbnailOverlayRenderer', 'content', 'musicPlayButtonRenderer'
]
NAVIGATION_BROWSE_ID = ['navigationEndpoint', 'browseEndpoint', 'browseId']
NAVIGATION_VIDEO_ID = ['navigationEndpoint', 'watchEndpoint', 'videoId']
NAVIGATION_PLAYLIST_ID = ['navigationEndpoint', 'watchEndpoint', 'playlistId']
CAROUSEL_TITLE = ['header', 'musicCarouselShelfBasicHeaderRenderer', 'title', 'runs', 0]
FRAMEWORK_MUTATIONS = ['frameworkUpdates', 'entityBatchUpdate', 'mutations']
TITLE = ['title', 'runs', 0]
TITLE_TEXT = ['title', 'runs', 0, 'text']
SUBTITLE = ['subtitle', 'runs', 0, 'text']
SUBTITLE2 = ['subtitle', 'runs', 2, 'text']
SUBTITLE3 = ['subtitle', 'runs', 4, 'text']
THUMBNAIL = ['thumbnail', 'thumbnails']
THUMBNAILS = ['thumbnail', 'musicThumbnailRenderer'] + THUMBNAIL
THUMBNAIL_RENDERER = ['thumbnailRenderer', 'musicThumbnailRenderer'] + THUMBNAIL
THUMBNAIL_CROPPED = ['thumbnail', 'croppedSquareThumbnailRenderer'] + THUMBNAIL
