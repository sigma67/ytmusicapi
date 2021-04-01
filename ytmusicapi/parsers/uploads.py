from .utils import *
from .songs import *


def parse_uploaded_items(results):
    songs = []
    for result in results:
        data = result['musicResponsiveListItemRenderer']
        if 'menu' not in data:
            continue
        entityId = nav(data, MENU_ITEMS)[-1]['menuNavigationItemRenderer']['navigationEndpoint'][
            'confirmDialogEndpoint']['content']['confirmDialogRenderer']['confirmButton'][
                'buttonRenderer']['command']['musicDeletePrivatelyOwnedEntityCommand']['entityId']

        videoId = nav(data, MENU_ITEMS + [0]
                      + MENU_SERVICE)['queueAddEndpoint']['queueTarget']['videoId']

        title = get_item_text(data, 0)
        like = nav(data, MENU_LIKE_STATUS)
        thumbnails = nav(data, THUMBNAILS) if 'thumbnail' in data else None
        duration = get_fixed_column_item(data, 0)['text']['runs'][0]['text']
        song = {
            'entityId': entityId,
            'videoId': videoId,
            'title': title,
            'duration': duration,
            'artist': None,
            'album': None,
            'likeStatus': like,
            'thumbnails': thumbnails
        }
        song['artist'] = parse_song_artists(data, 1)
        song['album'] = parse_song_album(data, 2)

        songs.append(song)

    return songs
