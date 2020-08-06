from .utils import *


def parse_watch_playlist(results):
    tracks = []
    for result in results:
        if 'playlistPanelVideoRenderer' not in result:
            continue
        data = result['playlistPanelVideoRenderer']
        if 'unplayableText' in data:
            continue
        track = {
            'title': nav(data, TITLE_TEXT),
            'byline': nav(data, ['shortBylineText', 'runs', 0, 'text'], True),
            'length': nav(data, ['lengthText', 'runs', 0, 'text']),
            'videoId': data['videoId'],
            'playlistId': nav(data, NAVIGATION_PLAYLIST_ID),
            'thumbnail': nav(data, THUMBNAIL)
        }
        tracks.append(track)
    return tracks
