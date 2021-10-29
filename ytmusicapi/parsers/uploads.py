from typing import List
from typing import Dict

from ytmusicapi.parsers.songs import MRLIR
from ytmusicapi.parsers.songs import THUMBNAILS
from ytmusicapi.parsers.songs import MENU_ITEMS
from ytmusicapi.parsers.songs import MENU_SERVICE
from ytmusicapi.parsers.songs import MENU_LIKE_STATUS

from ytmusicapi.parsers.songs import parse_song_album
from ytmusicapi.parsers.songs import parse_song_artists

from ytmusicapi.parsers.utils import nav
from ytmusicapi.parsers.utils import get_item_text
from ytmusicapi.parsers.utils import get_fixed_column_item


def parse_uploaded_items(results: list) -> List[Dict]:
    """Parses the uploaded items.

    ### Parameters
    results (list):
        A collection of `UploadedItems`.

    ### Returns
    ----
    List[Dict]:
        A collection of `Song` objects.
    """

    songs = []

    for result in results:
        data = result[MRLIR]

        if 'menu' not in data:
            continue

        nav_endpoint = nav(
            root=data,
            items=MENU_ITEMS
        )[-1]['menuNavigationItemRenderer']['navigationEndpoint']

        # Capture the entity ID.
        dia_render = nav_endpoint['confirmDialogEndpoint']['content']['confirmDialogRenderer']
        command = dia_render['confirmButton']['buttonRenderer']['command']
        entity_id = command['musicDeletePrivatelyOwnedEntityCommand']['entityId']

        # Capture the Video ID.
        video_id = nav(
            root=data,
            items=MENU_ITEMS + [0] + MENU_SERVICE
        )['queueAddEndpoint']['queueTarget']['videoId']

        title = get_item_text(data, 0)
        like = nav(data, MENU_LIKE_STATUS)
        thumbnails = nav(data, THUMBNAILS) if 'thumbnail' in data else None
        duration = get_fixed_column_item(data, 0)['text']['runs'][0]['text']
        song = {
            'entityId': entity_id,
            'videoId': video_id,
            'title': title,
            'duration': duration,
            'artists': None,
            'album': None,
            'likeStatus': like,
            'thumbnails': thumbnails
        }
        song['artists'] = parse_song_artists(data, 1)
        song['album'] = parse_song_album(data, 2)

        songs.append(song)

    return songs
