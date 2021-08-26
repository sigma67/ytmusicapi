from ytmusicapi.parsers.browsing import *

TRENDS = {'ARROW_DROP_UP': 'up', 'ARROW_DROP_DOWN': 'down', 'ARROW_CHART_NEUTRAL': 'neutral'}


def parse_chart_song(data):
    flex_0 = get_flex_column_item(data, 0)
    parsed = {
        'title': nav(flex_0, TEXT_RUN_TEXT),
        'videoId': nav(flex_0, TEXT_RUN + NAVIGATION_VIDEO_ID, True),
        'artists': parse_song_artists(data, 1),
        'thumbnails': nav(data, THUMBNAILS),
        'isExplicit': nav(data, BADGE_LABEL, True) == 'Explicit'
    }
    flex_2 = get_flex_column_item(data, 2)
    if flex_2 and 'navigationEndpoint' in nav(flex_2, TEXT_RUN):
        parsed['album'] = {
            'name': nav(flex_2, TEXT_RUN_TEXT),
            'id': nav(flex_2, TEXT_RUN + NAVIGATION_BROWSE_ID)
        }
    else:
        flex_1 = get_flex_column_item(data, 1)
        parsed['views'] = nav(flex_1, ['text', 'runs', -1, 'text']).split(' ')[0]
    parsed.update(parse_ranking(data))
    return parsed


def parse_chart_artist(data):
    subscribers = get_flex_column_item(data, 1)
    if subscribers:
        subscribers = nav(subscribers, TEXT_RUN_TEXT).split(' ')[0]

    parsed = {
        'title': nav(get_flex_column_item(data, 0), TEXT_RUN_TEXT),
        'browseId': nav(data, NAVIGATION_BROWSE_ID),
        'subscribers': subscribers,
        'thumbnails': nav(data, THUMBNAILS),
    }
    parsed.update(parse_ranking(data))
    return parsed


def parse_chart_trending(data):
    flex_0 = get_flex_column_item(data, 0)
    artists = parse_song_artists(data, 1)
    views = artists.pop()  # last item is views for some reason
    views = views['name'].split(' ')[0]
    return {
        'title': nav(flex_0, TEXT_RUN_TEXT),
        'videoId': nav(flex_0, TEXT_RUN + NAVIGATION_VIDEO_ID),
        'playlistId': nav(flex_0, TEXT_RUN + NAVIGATION_PLAYLIST_ID),
        'artists': artists,
        'thumbnails': nav(data, THUMBNAILS),
        'views': views
    }


def parse_ranking(data):
    return {
        'rank':
        nav(data, ['customIndexColumn', 'musicCustomIndexColumnRenderer'] + TEXT_RUN_TEXT),
        'trend':
        TRENDS[nav(data,
                   ['customIndexColumn', 'musicCustomIndexColumnRenderer', 'icon', 'iconType'])]
    }
