from .songs import *
from ._utils import *


def parse_mixed_content(rows):
    items = []
    for row in rows:
        if DESCRIPTION_SHELF[0] in row:
            results = nav(row, DESCRIPTION_SHELF)
            title = nav(results, ['header'] + RUN_TEXT)
            contents = nav(results, DESCRIPTION)
        else:
            results = next(iter(row.values()))
            if 'contents' not in results:
                continue
            title = nav(results, CAROUSEL_TITLE + ['text'])
            contents = []
            for result in results['contents']:
                data = nav(result, [MTRIR], True)
                content = None
                if data:
                    page_type = nav(data, TITLE + NAVIGATION_BROWSE + PAGE_TYPE, True)
                    if page_type is None:  # song or watch_playlist
                        if nav(data, NAVIGATION_WATCH_PLAYLIST_ID, True) is not None:
                            content = parse_watch_playlist(data)
                        else:
                            content = parse_song(data)
                    elif page_type == "MUSIC_PAGE_TYPE_ALBUM":
                        content = parse_album(data)
                    elif page_type == "MUSIC_PAGE_TYPE_ARTIST":
                        content = parse_related_artist(data)
                    elif page_type == "MUSIC_PAGE_TYPE_PLAYLIST":
                        content = parse_playlist(data)
                else:
                    data = nav(result, [MRLIR])
                    content = parse_song_flat(data)

                contents.append(content)

        items.append({'title': title, 'contents': contents})
    return items


def parse_content_list(results, parse_func, key=MTRIR):
    contents = []
    for result in results:
        contents.append(parse_func(result[key]))

    return contents


def parse_album(result):
    return {
        'title': nav(result, TITLE_TEXT),
        'year': nav(result, SUBTITLE2, True),
        'browseId': nav(result, TITLE + NAVIGATION_BROWSE_ID),
        'thumbnails': nav(result, THUMBNAIL_RENDERER),
        'isExplicit': nav(result, SUBTITLE_BADGE_LABEL, True) is not None
    }


def parse_single(result):
    return {
        'title': nav(result, TITLE_TEXT),
        'year': nav(result, SUBTITLE, True),
        'browseId': nav(result, TITLE + NAVIGATION_BROWSE_ID),
        'thumbnails': nav(result, THUMBNAIL_RENDERER)
    }


def parse_song(result):
    song = {
        'title': nav(result, TITLE_TEXT),
        'videoId': nav(result, NAVIGATION_VIDEO_ID),
        'playlistId': nav(result, NAVIGATION_PLAYLIST_ID, True),
        'thumbnails': nav(result, THUMBNAIL_RENDERER)
    }
    song.update(parse_song_runs(nav(result, SUBTITLE_RUNS)))
    return song


def parse_song_flat(data):
    columns = [get_flex_column_item(data, i) for i in range(0, len(data['flexColumns']))]
    song = {
        'title': nav(columns[0], TEXT_RUN_TEXT),
        'videoId': nav(columns[0], TEXT_RUN + NAVIGATION_VIDEO_ID, True),
        'artists': parse_song_artists(data, 1),
        'thumbnails': nav(data, THUMBNAILS),
        'isExplicit': nav(data, BADGE_LABEL, True) is not None
    }
    if len(columns) > 2 and columns[2] is not None and 'navigationEndpoint' in nav(
            columns[2], TEXT_RUN):
        song['album'] = {
            'name': nav(columns[2], TEXT_RUN_TEXT),
            'id': nav(columns[2], TEXT_RUN + NAVIGATION_BROWSE_ID)
        }
    else:
        song['views'] = nav(columns[1], ['text', 'runs', -1, 'text']).split(' ')[0]

    return song


def parse_video(result):
    runs = nav(result, SUBTITLE_RUNS)
    artists_len = get_dot_separator_index(runs)
    return {
        'title': nav(result, TITLE_TEXT),
        'videoId': nav(result, NAVIGATION_VIDEO_ID),
        'artists': parse_song_artists_runs(runs[:artists_len]),
        'playlistId': nav(result, NAVIGATION_PLAYLIST_ID, True),
        'thumbnails': nav(result, THUMBNAIL_RENDERER, True),
        'views': runs[-1]['text'].split(' ')[0]
    }


def parse_playlist(data):
    playlist = {
        'title': nav(data, TITLE_TEXT),
        'playlistId': nav(data, TITLE + NAVIGATION_BROWSE_ID)[2:],
        'thumbnails': nav(data, THUMBNAIL_RENDERER)
    }
    subtitle = data['subtitle']
    if 'runs' in subtitle:
        playlist['description'] = "".join([run['text'] for run in subtitle['runs']])
        if len(subtitle['runs']) == 3 and re.search(r'\d+ ', nav(data, SUBTITLE2)):
            playlist['count'] = nav(data, SUBTITLE2).split(' ')[0]
            playlist['author'] = parse_song_artists_runs(subtitle['runs'][:1])

    return playlist


def parse_related_artist(data):
    subscribers = nav(data, SUBTITLE, True)
    if subscribers:
        subscribers = subscribers.split(' ')[0]
    return {
        'title': nav(data, TITLE_TEXT),
        'browseId': nav(data, TITLE + NAVIGATION_BROWSE_ID),
        'subscribers': subscribers,
        'thumbnails': nav(data, THUMBNAIL_RENDERER),
    }


def parse_watch_playlist(data):
    return {
        'title': nav(data, TITLE_TEXT),
        'playlistId': nav(data, NAVIGATION_WATCH_PLAYLIST_ID),
        'thumbnails': nav(data, THUMBNAIL_RENDERER),
    }
