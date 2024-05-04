from typing import List, Optional

from ..helpers import to_int
from .songs import *


def parse_playlist_header(response: Dict) -> Dict[str, Any]:
    playlist: Dict[str, Any] = {}
    editable_header = nav(response, [*HEADER, *EDITABLE_PLAYLIST_DETAIL_HEADER], True)
    playlist["owned"] = editable_header is not None
    playlist["privacy"] = "PUBLIC"
    if editable_header is not None:  # owned playlist
        header = nav(editable_header, HEADER_DETAIL)
        playlist["privacy"] = editable_header["editHeader"]["musicPlaylistEditHeaderRenderer"]["privacy"]
    else:
        header = nav(response, HEADER_DETAIL, True)

    playlist["title"] = nav(header, TITLE_TEXT)
    playlist["thumbnails"] = nav(header, THUMBNAIL_CROPPED)
    playlist["description"] = nav(header, DESCRIPTION, True)
    run_count = len(nav(header, SUBTITLE_RUNS))
    if run_count > 1:
        playlist["author"] = {
            "name": nav(header, SUBTITLE2),
            "id": nav(header, [*SUBTITLE_RUNS, 2, *NAVIGATION_BROWSE_ID], True),
        }
        if run_count == 5:
            playlist["year"] = nav(header, SUBTITLE3)

    playlist["views"] = None
    playlist["duration"] = None
    playlist["trackCount"] = None
    if "runs" in header["secondSubtitle"]:
        second_subtitle_runs = header["secondSubtitle"]["runs"]
        has_views = (len(second_subtitle_runs) > 3) * 2
        playlist["views"] = None if not has_views else to_int(second_subtitle_runs[0]["text"])
        has_duration = (len(second_subtitle_runs) > 1) * 2
        playlist["duration"] = (
            None if not has_duration else second_subtitle_runs[has_views + has_duration]["text"]
        )
        song_count = second_subtitle_runs[has_views + 0]["text"].split(" ")
        song_count = to_int(song_count[0]) if len(song_count) > 1 else 0
        playlist["trackCount"] = song_count

    return playlist


def parse_playlist_items(results, menu_entries: Optional[List[List]] = None, is_album=False):
    songs = []
    for result in results:
        if MRLIR not in result:
            continue
        data = result[MRLIR]
        song = parse_playlist_item(data, menu_entries, is_album)
        if song:
            songs.append(song)

    return songs


def parse_playlist_item(
    data: Dict, menu_entries: Optional[List[List]] = None, is_album=False
) -> Optional[Dict]:
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
                    setVideoId = nav(menu_service, ["playlistEditEndpoint", "actions", 0, "setVideoId"], True)
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
        return None

    flex_column_count = len(data["flexColumns"])

    artists = parse_song_artists(data, 1)

    album = parse_song_album(data, flex_column_count - 1) if not is_album else None

    views = get_item_text(data, 2) if flex_column_count == 4 or is_album else None

    duration = None
    if "fixedColumns" in data:
        if "simpleText" in get_fixed_column_item(data, 0)["text"]:
            duration = get_fixed_column_item(data, 0)["text"]["simpleText"]
        else:
            duration = get_fixed_column_item(data, 0)["text"]["runs"][0]["text"]

    thumbnails = nav(data, THUMBNAILS, True)

    isAvailable = True
    if "musicItemRendererDisplayPolicy" in data:
        isAvailable = data["musicItemRendererDisplayPolicy"] != "MUSIC_ITEM_RENDERER_DISPLAY_POLICY_GREY_OUT"

    isExplicit = nav(data, BADGE_LABEL, True) is not None

    videoType = nav(
        data,
        [*MENU_ITEMS, 0, MNIR, "navigationEndpoint", *NAVIGATION_VIDEO_TYPE],
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

    if is_album:
        song["trackNumber"] = int(nav(data, ["index", "runs", 0, "text"])) if isAvailable else None

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

    return song


def validate_playlist_id(playlistId: str) -> str:
    return playlistId if not playlistId.startswith("VL") else playlistId[2:]
