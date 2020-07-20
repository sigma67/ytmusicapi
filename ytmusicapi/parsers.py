from ytmusicapi.helpers import i18n
# commonly used navigation paths
SINGLE_COLUMN_TAB = [
    'contents', 'singleColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content'
]
SECTION_LIST = ['sectionListRenderer', 'contents']
ITEM_SECTION = ['itemSectionRenderer', 'contents', 0]
MUSIC_SHELF = [0, 'musicShelfRenderer']
CONTINUATION = ['continuations', 0, 'nextContinuationData', 'continuation']
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
THUMBNAILS = ['thumbnail', 'musicThumbnailRenderer', 'thumbnail', 'thumbnails']
THUMBNAIL_RENDERER = ['thumbnailRenderer', 'musicThumbnailRenderer', 'thumbnail', 'thumbnails']
THUMBNAIL_CROPPED = ['thumbnail', 'croppedSquareThumbnailRenderer', 'thumbnail', 'thumbnails']


class Parser:
    def __init__(self, language):
        self.lang = language

    @i18n
    def parse_search_result(self, data, resultType=None):
        search_result = {}
        default = not resultType
        if not resultType:
            resultType = get_item_text(data, 1).lower()
            result_types = ['artist', 'playlist', 'song', 'video']
            result_types_local = [_('artist'), _('playlist'), _('song'), _('video')]
            # default to album since it's labeled with multiple values ('Single', 'EP', etc.)
            if resultType not in result_types_local:
                resultType = 'album'
            else:
                resultType = result_types[result_types_local.index(resultType)]

        if resultType in ['song', 'video']:
            search_result['videoId'] = nav(
                data, PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']
            search_result['title'] = get_item_text(data, 0)

        if resultType in ['artist', 'album', 'playlist']:
            search_result['browseId'] = nav(data, NAVIGATION_BROWSE_ID)

        if resultType in ['artist']:
            search_result['artist'] = get_item_text(data, 0)

        elif resultType in ['album']:
            search_result['title'] = get_item_text(data, 0)
            search_result['type'] = get_item_text(data, 1)
            search_result['artist'] = get_item_text(data, 2)
            search_result['year'] = get_item_text(data, 3)

        elif resultType in ['playlist']:
            search_result['title'] = get_item_text(data, 0)
            search_result['author'] = get_item_text(data, 1 + default)
            search_result['itemCount'] = get_item_text(data, 2 + default).split(' ')[0]

        elif resultType in ['song']:
            search_result['artists'] = parse_song_artists(data, 1 + default)
            hasAlbum = len(data['flexColumns']) == 4 + default
            if hasAlbum:
                search_result['album'] = parse_song_album(data, 2 + default)
            search_result['duration'] = get_item_text(data, 2 + hasAlbum + default)

        elif resultType in ['video']:
            search_result['artist'] = get_item_text(data, 1 + default)
            search_result['views'] = get_item_text(data, 2 + default).split(' ')[0]
            search_result['duration'] = get_item_text(data, 3 + default)

        search_result['thumbnails'] = nav(data, THUMBNAILS)
        search_result['resultType'] = resultType

        return search_result


def parse_playlists(results):
    playlists = []
    for result in results:
        data = result['musicTwoRowItemRenderer']
        playlist = {}
        playlist['playlistId'] = nav(data, TITLE + NAVIGATION_BROWSE_ID)[2:]
        playlist['title'] = nav(data, TITLE_TEXT)
        playlist['thumbnails'] = nav(data, THUMBNAIL_RENDERER)
        if len(data['subtitle']['runs']) == 3:
            playlist['count'] = nav(data, SUBTITLE2).split(' ')[0]

        playlists.append(playlist)

    return playlists


def parse_artists(results, uploaded=False):
    artists = []
    for result in results:
        data = result['musicResponsiveListItemRenderer']
        artist = {}
        artist['browseId'] = nav(data, NAVIGATION_BROWSE_ID)
        artist['artist'] = get_item_text(data, 0)
        if uploaded:
            artist['songs'] = get_item_text(data, 1).split(' ')[0]
        else:
            subtitle = get_item_text(data, 1)
            if subtitle:
                artist['subscribers'] = subtitle.split(' ')[0]
        artist['thumbnails'] = nav(data, THUMBNAILS)
        artists.append(artist)

    return artists


def parse_albums(results, upload=True):
    albums = []
    for result in results:
        data = result['musicTwoRowItemRenderer']
        album = {}
        album['browseId'] = nav(data, TITLE + NAVIGATION_BROWSE_ID)
        album['title'] = nav(data, TITLE_TEXT)
        album['type'] = nav(data, SUBTITLE)
        album['thumbnails'] = nav(data, THUMBNAIL_RENDERER)
        album['artists'] = []
        run_count = len(data['subtitle']['runs'])
        has_artists = False
        if upload:
            if run_count == 3:
                if nav(data, SUBTITLE2).isdigit():
                    album['year'] = nav(data, SUBTITLE2)
                else:
                    has_artists = True

            elif run_count > 3:
                album['year'] = nav(data, SUBTITLE3)
                has_artists = True

            if has_artists:
                subtitle = data['subtitle']['runs'][2]
                album['artists'].append({
                    'name': subtitle['text'],
                    'id': nav(subtitle, NAVIGATION_BROWSE_ID)
                })
        else:
            album['artists'] = nav(data, SUBTITLE)
            album['year'] = nav(data, SUBTITLE2)
            album['trackCount'] = nav(data, SUBTITLE3).split(' ')[0]

        albums.append(album)

    return albums


def parse_playlist_items(results):
    songs = []
    count = 1
    for result in results:
        count += 1
        if 'musicResponsiveListItemRenderer' not in result:
            continue
        data = result['musicResponsiveListItemRenderer']

        try:
            # if playlist is not owned, the playlist item can't be interacted with
            videoId = setVideoId = None
            like = None

            # if item is not playable, there is no videoId
            if 'playNavigationEndpoint' in nav(data, PLAY_BUTTON):
                videoId = nav(data,
                              PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']

                for item in nav(data, MENU_ITEMS):
                    if 'menuServiceItemRenderer' in item and 'playlistEditEndpoint' in nav(
                            item, MENU_SERVICE):
                        setVideoId = nav(
                            item, MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['setVideoId']
                        break

                if 'menu' in data:
                    like = nav(data, MENU_LIKE_STATUS, True)

            title = get_item_text(data, 0)
            if title == 'Song deleted':
                continue

            artists = parse_song_artists(data, 1)

            album = parse_song_album(data, 2)

            duration = None
            if 'fixedColumns' in data:
                if 'simpleText' in data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']:
                    duration = data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']['simpleText']
                else:
                    duration = data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']['runs'][0]['text']

            thumbnails = None
            if 'thumbnail' in data:
                thumbnails = nav(data, THUMBNAILS)

            song = {
                'videoId': videoId,
                'title': title,
                'artists': artists,
                'album': album,
                'likeStatus': like,
                'thumbnails': thumbnails
            }
            if duration:
                song['duration'] = duration
            if setVideoId:
                song['setVideoId'] = setVideoId

            songs.append(song)

        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs


def parse_uploaded_items(results):
    songs = []
    for result in results:
        data = result['musicResponsiveListItemRenderer']
        if 'menu' not in data:
            continue
        entityId = nav(data, MENU_ITEMS)[-1]['menuNavigationItemRenderer']['navigationEndpoint'][
            'confirmDialogEndpoint']['content']['confirmDialogRenderer']['confirmButton'][
                'buttonRenderer']['command']['musicDeletePrivatelyOwnedEntityCommand']['entityId']

        videoId = nav(data, MENU_ITEMS + [0]
                      + MENU_SERVICE)['queueAddEndpoint']['queueTarget']['videoId']

        title = get_item_text(data, 0)
        like = nav(data, MENU_LIKE_STATUS)
        thumbnails = nav(data, THUMBNAILS) if 'thumbnail' in data else None
        song = {
            'entityId': entityId,
            'videoId': videoId,
            'title': title,
            'artist': None,
            'album': None,
            'likeStatus': like,
            'thumbnails': thumbnails
        }
        if get_flex_column_item(data, 1):
            song['artist'] = parse_song_artists(data, 1)
            song['album'] = parse_song_album(data, 2)

        songs.append(song)

    return songs


def parse_library_artists(response, request_func, limit):
    results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                 'itemSectionRenderer')
    results = nav(results, ITEM_SECTION)
    if 'musicShelfRenderer' not in results:
        return []
    results = results['musicShelfRenderer']
    artists = parse_artists(results['contents'])

    if 'continuations' in results:
        parse_func = lambda contents: parse_artists(contents)
        artists.extend(
            get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                              parse_func))

    return artists


def parse_song_artists(data, index):
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return None
    artists = []
    for j in range(int(len(flex_item['text']['runs']) / 2) + 1):
        artists.append({
            'name': get_item_text(data, index, j * 2),
            'id': get_browse_id(flex_item, j * 2)
        })

    return artists


def parse_song_album(data, index):
    flex_item = get_flex_column_item(data, index)
    return None if not flex_item else {
        'name': get_item_text(data, index),
        'id': get_browse_id(flex_item, 0)
    }


def get_item_text(item, index, run_index=0):
    column = get_flex_column_item(item, index)
    return column if not column else column['text']['runs'][run_index]['text']


def get_flex_column_item(item, index):
    if 'text' not in item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer'] or \
            'runs' not in item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']['text']:
        return None

    return item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']


def get_browse_id(item, index):
    if 'navigationEndpoint' not in item['text']['runs'][index]:
        return None
    else:
        return nav(item['text']['runs'][index], NAVIGATION_BROWSE_ID)


def get_continuations(results, continuation_type, per_page, limit, request_func, parse_func):
    items = []
    while 'continuations' in results and len(items) < limit - per_page:
        ctoken = nav(results, CONTINUATION)
        additionalParams = "&ctoken=" + ctoken + "&continuation=" + ctoken
        response = request_func(additionalParams)
        results = response['continuationContents'][continuation_type]
        continuation_contents = 'contents' if 'Shelf' in continuation_type else 'items'
        items.extend(parse_func(results[continuation_contents]))

    return items


def nav(root, items, none_if_absent=False):
    """Access a nested object in root by item sequence."""
    try:
        for k in items:
            root = root[k]
        return root
    except KeyError as err:
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
