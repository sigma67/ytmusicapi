from .utils import *
from .songs import *


def parse_watch_playlist(results):
    tracks = []
    for result in results:
        if 'playlistPanelVideoRenderer' not in result:
            continue
        data = result['playlistPanelVideoRenderer']
        if 'unplayableText' in data:
            continue

        feedback_tokens = like_status = None
        for item in nav(data, MENU_ITEMS):
            if TOGGLE_MENU in item:
                service = item[TOGGLE_MENU]['defaultServiceEndpoint']
                if 'feedbackEndpoint' in service:
                    feedback_tokens = parse_song_menu_tokens(item)
                if 'likeEndpoint' in service:
                    like_status = parse_like_status(service)

        song_info = parse_song_runs(data['longBylineText']['runs'])

        track = {
            'videoId': data['videoId'],
            'title': nav(data, TITLE_TEXT),
            'length': nav(data, ['lengthText', 'runs', 0, 'text'], True),
            'thumbnail': nav(data, THUMBNAIL),
            'feedbackTokens': feedback_tokens,
            'likeStatus': like_status
        }
        track.update(song_info)
        tracks.append(track)

    return tracks
