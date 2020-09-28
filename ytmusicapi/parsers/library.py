from .playlists import parse_playlist_items
from .utils import *


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
            album['artists'] = {
                'name': nav(data, SUBTITLE2),
                'id': nav(data, ['subtitle', 'runs', 2] + NAVIGATION_BROWSE_ID, True)
            }
            album['year'] = nav(data, SUBTITLE3)

        albums.append(album)

    return albums


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
            get_continuations(results, 'musicShelfContinuation', limit - len(artists),
                              request_func, parse_func))

    return artists


def parse_library_songs(response):
    results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                 'itemSectionRenderer')
    results = nav(results, ITEM_SECTION)
    songs = {'results': [], 'parsed': []}
    if 'musicShelfRenderer' in results:
        songs['results'] = results['musicShelfRenderer']
        songs['parsed'] = parse_playlist_items(songs['results']['contents'][1:])

    return songs
