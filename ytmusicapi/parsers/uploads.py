from ytmusicapi.type_alias import JsonList

from ._utils import *
from .songs import parse_song_album, parse_song_artists


def parse_uploaded_items(results: JsonList) -> JsonList:
    songs = []
    for result in results:
        data = result[MRLIR]
        if "menu" not in data:
            continue
        entityId = nav(
            data,
            [
                *MENU_ITEMS,
                -1,
                MNIR,
                "navigationEndpoint",
                "confirmDialogEndpoint",
                "content",
                "confirmDialogRenderer",
                "confirmButton",
                "buttonRenderer",
                "command",
                "musicDeletePrivatelyOwnedEntityCommand",
                "entityId",
            ],
        )
        videoId = nav(data, [*MENU_ITEMS, 0, *MENU_SERVICE])["queueAddEndpoint"]["queueTarget"]["videoId"]

        title = get_item_text(data, 0)
        like = nav(data, MENU_LIKE_STATUS)
        thumbnails = nav(data, THUMBNAILS) if "thumbnail" in data else None
        duration = None
        if "fixedColumns" in data:
            duration = nav(get_fixed_column_item(data, 0), TEXT_RUN_TEXT)
        song = {
            "entityId": entityId,
            "videoId": videoId,
            "title": title,
            "duration": duration,
            "duration_seconds": parse_duration(duration),
            "artists": parse_song_artists(data, 1),
            "album": parse_song_album(data, 2),
            "likeStatus": like,
            "thumbnails": thumbnails,
        }

        songs.append(song)

    return songs
