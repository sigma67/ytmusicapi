from .utils import *


def parse_watch_playlist(results):
    tracks = []
    for result in results:
        if 'playlistPanelVideoRenderer' not in result:
            continue
        data = result['playlistPanelVideoRenderer']
        if 'unplayableText' in data:
            continue

        feedback_tokens = None
        for item in nav(data, MENU_ITEMS):
            if 'toggleMenuServiceItemRenderer' in item:
                feedback_tokens = parse_song_menu_tokens(item)
                break

        runs = data['longBylineText']['runs']
        last_artist_index = get_last_artist_index(runs)
        artists = parse_song_artists_runs(runs[:last_artist_index + 1])
        album = parse_song_album_runs(runs, last_artist_index)

        track = {
            'videoId': data['videoId'],
            'title': nav(data, TITLE_TEXT),
            'artists': artists,
            'album': album,
            'length': nav(data, ['lengthText', 'runs', 0, 'text']),
            'playlistId': nav(data, NAVIGATION_PLAYLIST_ID),
            'thumbnail': nav(data, THUMBNAIL),
            'feedbackTokens': feedback_tokens
        }
        tracks.append(track)

    return tracks
