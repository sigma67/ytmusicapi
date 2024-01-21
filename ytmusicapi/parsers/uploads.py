from ._utils import *
from .songs import parse_song_album, parse_song_artists


def parse_uploaded_items(results):
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
        duration = get_fixed_column_item(data, 0)["text"]["runs"][0]["text"]
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
