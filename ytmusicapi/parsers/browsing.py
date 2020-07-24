from typing import List, Dict
from .utils import *
from ytmusicapi.helpers import i18n


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

    @i18n
    def parse_artist_contents(self, results: List) -> Dict:
        categories = ['albums', 'singles', 'videos', 'playlists']
        categories_local = [_('albums'), _('singles'), _('videos'), _('playlists')]
        categories_parser = [parse_album, parse_single, parse_video, parse_playlist]
        artist = {}
        for i, category in enumerate(categories):
            data = [
                r['musicCarouselShelfRenderer'] for r in results
                if 'musicCarouselShelfRenderer' in r
                and nav(r['musicCarouselShelfRenderer'],
                        CAROUSEL_TITLE)['text'].lower() == categories_local[i]
            ]
            if len(data) > 0:
                artist[category] = {'browseId': None, 'results': []}
                if 'navigationEndpoint' in nav(data[0], CAROUSEL_TITLE):
                    artist[category]['browseId'] = nav(data[0],
                                                       CAROUSEL_TITLE + NAVIGATION_BROWSE_ID)
                    if category in ['albums', 'singles', 'playlists']:
                        artist[category]['params'] = nav(
                            data[0],
                            CAROUSEL_TITLE)['navigationEndpoint']['browseEndpoint']['params']

                artist[category]['results'] = parse_content_list(data[0]['contents'],
                                                                 categories_parser[i])

        return artist


def parse_content_list(results, parse_func):
    contents = []
    for result in results:
        contents.append(parse_func(result['musicTwoRowItemRenderer']))

    return contents


def parse_album(result):
    return {
        'title': nav(result, TITLE_TEXT),
        'year': nav(result, SUBTITLE2, True),
        'browseId': nav(result, TITLE + NAVIGATION_BROWSE_ID),
        'thumbnails': nav(result, THUMBNAIL_RENDERER)
    }


def parse_single(result):
    return {
        'title': nav(result, TITLE_TEXT),
        'year': nav(result, SUBTITLE, True),
        'browseId': nav(result, TITLE + NAVIGATION_BROWSE_ID),
        'thumbnails': nav(result, THUMBNAIL_RENDERER)
    }


def parse_video(result):
    video = {
        'title': nav(result, TITLE_TEXT),
        'videoId': nav(result, NAVIGATION_VIDEO_ID),
        'playlistId': nav(result, NAVIGATION_PLAYLIST_ID),
        'thumbnails': nav(result, THUMBNAIL_RENDERER)
    }
    if len(result['subtitle']['runs']) == 3:
        video['views'] = nav(result, SUBTITLE2).split(' ')[0]
    return video


def parse_playlist(data):
    playlist = {
        'title': nav(data, TITLE_TEXT),
        'playlistId': nav(data, TITLE + NAVIGATION_BROWSE_ID)[2:],
        'thumbnails': nav(data, THUMBNAIL_RENDERER)
    }
    if len(data['subtitle']['runs']) == 3:
        playlist['count'] = nav(data, SUBTITLE2).split(' ')[0]
    return playlist
