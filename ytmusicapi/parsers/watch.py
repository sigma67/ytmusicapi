from .utils import *


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
            if 'toggleMenuServiceItemRenderer' in item:
                service = item['toggleMenuServiceItemRenderer']['defaultServiceEndpoint']
                if 'feedbackEndpoint' in service:
                    feedback_tokens = parse_song_menu_tokens(item)
                if 'likeEndpoint' in service:
                    status = ['LIKE', 'INDIFFERENT']
                    like_status = status[status.index(service['likeEndpoint']['status']) - 1]

        runs = data['longBylineText']['runs']
        last_artist_index = get_last_artist_index(runs)
        artists = parse_song_artists_runs(runs[:last_artist_index + 1])
        album = parse_song_album_runs(runs, last_artist_index)

        track = {
            'videoId': data['videoId'],
            'title': nav(data, TITLE_TEXT),
            'artists': artists,
            'album': album,
            'length': nav(data, ['lengthText', 'runs', 0, 'text'], True),
            'playlistId': nav(data, NAVIGATION_PLAYLIST_ID),
            'thumbnail': nav(data, THUMBNAIL),
            'feedbackTokens': feedback_tokens,
            'likeStatus': like_status
        }
        tracks.append(track)

    return tracks
