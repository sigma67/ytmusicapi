import re
from http.cookies import SimpleCookie
from hashlib import sha1
import time

#commonly used navigation paths
SINGLE_COLUMN_TAB = ['contents', 'singleColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content']
SECTION_LIST = ['sectionListRenderer', 'contents']
ITEM_SECTION = ['itemSectionRenderer', 'contents', 0]
CONTINUATION = ['continuations', 0, 'nextContinuationData', 'continuation']
MENU_ITEMS = ['menu', 'menuRenderer', 'items']
MENU_SERVICE = ['menuServiceItemRenderer', 'serviceEndpoint']
PLAY_BUTTON = ['overlay', 'musicItemThumbnailOverlayRenderer', 'content', 'musicPlayButtonRenderer']
CAROUSEL_TITLE = ['header', 'musicCarouselShelfBasicHeaderRenderer', 'title', 'runs', 0]
FRAMEWORK_MUTATIONS = ['frameworkUpdates', 'entityBatchUpdate', 'mutations']

def nav(root, items):
    """Access a nested object in root by item sequence."""
    for k in items: root = root[k]
    return root


def parse_playlist_items(results, owned=False):
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
            if owned:
                for item in nav(data, MENU_ITEMS):
                    if 'menuServiceItemRenderer' in item and 'playlistEditEndpoint' in nav(item, MENU_SERVICE):
                        setVideoId = nav(item, MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['setVideoId']
                        videoId = nav(item, MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['removedVideoId']
                        break
            else:
                # if item is not playable, there is no videoId
                if 'playNavigationEndpoint' in nav(data, PLAY_BUTTON):
                    videoId = nav(data, PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']

            runs = [None] * 3
            for i in range(len(runs)):
                if 'text' in data['flexColumns'][i]['musicResponsiveListItemFlexColumnRenderer']:
                    runs[i] = get_item_text(data, i)

            duration = None
            if 'fixedColumns' in data:
                duration = data['fixedColumns'][0]['musicResponsiveListItemFixedColumnRenderer']['text']['simpleText']

            song = {'videoId': videoId, 'title': runs[0], 'artist': runs[1], 'album': runs[2]}
            if duration:
                song['duration'] = duration
            if owned:
                song['setVideoId'] = setVideoId

            songs.append(song)

        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs

def parse_uploaded_items(results):
    songs = []
    for result in results:
        data = result['musicResponsiveListItemRenderer']
        entityId = nav(data, MENU_ITEMS)[-1]['menuNavigationItemRenderer']['navigationEndpoint'][
            'confirmDialogEndpoint']['content']['confirmDialogRenderer']['confirmButton']['buttonRenderer']['command'][
            'musicDeletePrivatelyOwnedEntityCommand']['entityId']

        videoId = nav(data, MENU_ITEMS + [0] + MENU_SERVICE)['queueAddEndpoint']['queueTarget']['videoId']

        title = get_item_text(data, 0)
        artist = get_item_text(data, 1)
        album = get_item_text(data, 2)

        song = {'entityId': entityId, 'videoId': videoId, 'artist': artist, 'title': title, 'album': album}
        songs.append(song)

    return songs


def parse_search_result(data, resultType = None):
    search_result = {}
    default = not resultType
    if not resultType:
        resultType = get_item_text(data, 1).lower()
        # default to album since it's labeled with multiple values ('Single', 'EP', etc.)
        if resultType not in ['artist', 'playlist', 'song', 'video']:
            resultType = 'album'

    if resultType in ['song', 'video']:
        search_result['videoId'] = nav(data, PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']
        search_result['title'] = get_item_text(data, 0)
        search_result['artist'] = get_item_text(data, 1 + default)

    if resultType in ['artist', 'album', 'playlist']:
        search_result['browseId'] = data['navigationEndpoint']['browseEndpoint']['browseId']

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
        hasAlbum = len(data['flexColumns']) == 4
        if hasAlbum:
            search_result['album'] = get_item_text(data, 2 + default)
        search_result['duration'] = get_item_text(data, 2 + hasAlbum + default)

    elif resultType in ['video']:
        search_result['views'] = get_item_text(data, 2 + default).split(' ')[0]
        search_result['duration'] = get_item_text(data, 3 + default)

    search_result['resultType'] = resultType

    return search_result


def get_item_text(item, index, run_index=0):
    if 'runs' not in item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']['text']:
        return None

    return item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][run_index]['text']


def prepare_browse_endpoint(type, browseId):
    return {
        'browseEndpointContextSupportedConfigs':
        {
            "browseEndpointContextMusicConfig":
                {
                    "pageType": "MUSIC_PAGE_TYPE_" + type
                }
        },
        'browseId': browseId
    }


def html_to_txt(html_text):
    tags = re.findall("<[^>]+>",html_text)
    for tag in tags:
        html_text = html_text.replace(tag,'')
    return html_text


def sapisid_from_cookie(raw_cookie):
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    return cookie['SAPISID'].value


# SAPISID Hash reverse engineered by
# https://stackoverflow.com/a/32065323/5726546
def get_authorization(auth):
    sha_1 = sha1()
    unix_timestamp = str(int(time.time()))
    sha_1.update((unix_timestamp + ' ' + auth).encode('utf-8'))
    return "SAPISIDHASH " + unix_timestamp + "_" + sha_1.hexdigest()