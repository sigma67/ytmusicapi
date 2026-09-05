from ytmusicapi.helpers import sum_total_duration
from ytmusicapi.models.uploads import AlbumRef, ArtistRef, UploadAlbum, UploadSong
from ytmusicapi.type_alias import JsonDict, JsonList

from ._utils import *
from .albums import parse_album_header
from .songs import parse_song_album, parse_song_artists


def parse_uploaded_items(results: JsonList) -> list[UploadSong]:
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
        thumbnails = nav(data, THUMBNAILS, True)
        duration = None
        if "fixedColumns" in data:
            duration = nav(get_fixed_column_item(data, 0), TEXT_RUN_TEXT)
        song = UploadSong(
            entityId=entityId,
            videoId=videoId,
            title=title,
            duration=duration,
            duration_seconds=parse_duration(duration),
            artists=[ArtistRef(**artist) for artist in parse_song_artists(data, 1)],
            album=AlbumRef(**album) if (album := parse_song_album(data, 2)) else None,
            likeStatus=like,
            thumbnails=thumbnails,
        )

        songs.append(song)

    return songs


def parse_upload_album(response: JsonDict) -> UploadAlbum:
    album = parse_album_header(response)
    results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
    album["tracks"] = parse_uploaded_items(results["contents"])
    album["duration_seconds"] = sum_total_duration(album)
    return UploadAlbum(**album)
