from .playlists import parse_playlist_items
from ._utils import *
from ytmusicapi.continuations import get_continuations


def parse_artists(results, uploaded=False):
    artists = []
    for result in results:
        data = result[MRLIR]
        artist = {}
        artist['browseId'] = nav(data, NAVIGATION_BROWSE_ID)
        artist['artist'] = get_item_text(data, 0)
        parse_menu_playlists(data, artist)
        if uploaded:
            artist['songs'] = get_item_text(data, 1).split(' ')[0]
        else:
            subtitle = get_item_text(data, 1)
            if subtitle:
                artist['subscribers'] = subtitle.split(' ')[0]
        artist['thumbnails'] = nav(data, THUMBNAILS, True)
        artists.append(artist)

    return artists


def parse_library_albums(response, request_func, limit):
    results = get_library_contents(response, GRID)
    if results is None:
        return []
    albums = parse_albums(results['items'])

    if 'continuations' in results:
        parse_func = lambda contents: parse_albums(contents)
        remaining_limit = None if limit is None else (limit - len(albums))
        albums.extend(
            get_continuations(results, 'gridContinuation', remaining_limit, request_func,
                              parse_func))

    return albums


def parse_albums(results):
    albums = []
    for result in results:
        data = result[MTRIR]
        album = {}
        album['browseId'] = nav(data, TITLE + NAVIGATION_BROWSE_ID)
        album['title'] = nav(data, TITLE_TEXT)
        album['thumbnails'] = nav(data, THUMBNAIL_RENDERER)

        if 'runs' in data['subtitle']:
            run_count = len(data['subtitle']['runs'])
            has_artists = False
            if run_count == 1:
                album['year'] = nav(data, SUBTITLE)
            else:
                album['type'] = nav(data, SUBTITLE)

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
                album['artists'] = []
                album['artists'].append({
                    'name': subtitle['text'],
                    'id': nav(subtitle, NAVIGATION_BROWSE_ID, True)
                })

        albums.append(album)

    return albums


def parse_library_artists(response, request_func, limit):
    results = get_library_contents(response, MUSIC_SHELF)
    if results is None:
        return []
    artists = parse_artists(results['contents'])

    if 'continuations' in results:
        parse_func = lambda contents: parse_artists(contents)
        remaining_limit = None if limit is None else (limit - len(artists))
        artists.extend(
            get_continuations(results, 'musicShelfContinuation', remaining_limit, request_func,
                              parse_func))

    return artists


def parse_library_songs(response):
    results = get_library_contents(response, MUSIC_SHELF)
    return {'results': results, 'parsed': (parse_playlist_items(results['contents'][1:]))}


def get_library_contents(response, renderer):
    # first 3 lines are original path prior to #301
    contents = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST, True)
    if contents is None:  # empty library
        return None
    results = find_object_by_key(contents, 'itemSectionRenderer')
    if results is None:
        return nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + renderer, True)
    else:
        return nav(results, ITEM_SECTION + renderer)
