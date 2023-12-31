from typing import List

from ._utils import *
from .songs import *


def parse_playlist_items(results, menu_entries: List[List] = None):
    songs = []
    for result in results:
        if MRLIR not in result:
            continue
        data = result[MRLIR]

        videoId = setVideoId = None
        like = None
        feedback_tokens = None
        library_status = None

        # if the item has a menu, find its setVideoId
        if "menu" in data:
            for item in nav(data, MENU_ITEMS):
                if "menuServiceItemRenderer" in item:
                    menu_service = nav(item, MENU_SERVICE)
                    if "playlistEditEndpoint" in menu_service:
                        setVideoId = nav(
                            menu_service, ["playlistEditEndpoint", "actions", 0, "setVideoId"], True
                        )
                        videoId = nav(
                            menu_service, ["playlistEditEndpoint", "actions", 0, "removedVideoId"], True
                        )

                if TOGGLE_MENU in item:
                    feedback_tokens = parse_song_menu_tokens(item)
                    library_status = parse_song_library_status(item)

        # if item is not playable, the videoId was retrieved above
        if nav(data, PLAY_BUTTON, none_if_absent=True) is not None:
            if "playNavigationEndpoint" in nav(data, PLAY_BUTTON):
                videoId = nav(data, PLAY_BUTTON)["playNavigationEndpoint"]["watchEndpoint"]["videoId"]

                if "menu" in data:
                    like = nav(data, MENU_LIKE_STATUS, True)

        title = get_item_text(data, 0)
        if title == "Song deleted":
            continue

        artists = parse_song_artists(data, 1)

        album = parse_song_album(data, 2)

        views = None
        if album and album["id"] is None:
            # views currently only present on albums and formatting is localization-dependent -> no parsing
            if (views := (get_item_text(data, 2))) is not None:
                album = None

        duration = None
        if "fixedColumns" in data:
            if "simpleText" in get_fixed_column_item(data, 0)["text"]:
                duration = get_fixed_column_item(data, 0)["text"]["simpleText"]
            else:
                duration = get_fixed_column_item(data, 0)["text"]["runs"][0]["text"]

        thumbnails = None
        if "thumbnail" in data:
            thumbnails = nav(data, THUMBNAILS)

        isAvailable = True
        if "musicItemRendererDisplayPolicy" in data:
            isAvailable = (
                data["musicItemRendererDisplayPolicy"] != "MUSIC_ITEM_RENDERER_DISPLAY_POLICY_GREY_OUT"
            )

        isExplicit = nav(data, BADGE_LABEL, True) is not None

        videoType = nav(
            data,
            MENU_ITEMS + [0, "menuNavigationItemRenderer", "navigationEndpoint"] + NAVIGATION_VIDEO_TYPE,
            True,
        )

        song = {
            "videoId": videoId,
            "title": title,
            "artists": artists,
            "album": album,
            "likeStatus": like,
            "inLibrary": library_status,
            "thumbnails": thumbnails,
            "isAvailable": isAvailable,
            "isExplicit": isExplicit,
            "videoType": videoType,
            "views": views,
        }
        if duration:
            song["duration"] = duration
            song["duration_seconds"] = parse_duration(duration)
        if setVideoId:
            song["setVideoId"] = setVideoId
        if feedback_tokens:
            song["feedbackTokens"] = feedback_tokens

        if menu_entries:
            for menu_entry in menu_entries:
                song[menu_entry[-1]] = nav(data, MENU_ITEMS + menu_entry)

        songs.append(song)

    return songs


def validate_playlist_id(playlistId):
    return playlistId if not playlistId.startswith("VL") else playlistId[2:]
