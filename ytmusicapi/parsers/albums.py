from ytmusicapi.helpers import to_int
from ytmusicapi.type_alias import JsonDict

from ._utils import *
from .podcasts import parse_base_header
from .songs import parse_like_status, parse_song_runs


def parse_album_header(response: JsonDict) -> JsonDict:
    header = nav(response, HEADER_DETAIL)
    album = {
        "title": nav(header, TITLE_TEXT),
        "type": nav(header, SUBTITLE),
        "thumbnails": nav(header, THUMBNAIL_CROPPED),
        "isExplicit": nav(header, SUBTITLE_BADGE_LABEL, True) is not None,
    }

    if "description" in header:
        album["description"] = header["description"]["runs"][0]["text"]

    album_info = parse_song_runs(header["subtitle"]["runs"][2:])
    album.update(album_info)

    if len(header["secondSubtitle"]["runs"]) > 1:
        album["trackCount"] = to_int(header["secondSubtitle"]["runs"][0]["text"])
        album["duration"] = header["secondSubtitle"]["runs"][2]["text"]
    else:
        album["duration"] = header["secondSubtitle"]["runs"][0]["text"]

    # add to library/uploaded
    menu = nav(header, MENU)
    toplevel = menu["topLevelButtons"]
    album["audioPlaylistId"] = nav(toplevel, [0, "buttonRenderer", *NAVIGATION_WATCH_PLAYLIST_ID], True)
    if not album["audioPlaylistId"]:
        album["audioPlaylistId"] = nav(toplevel, [0, "buttonRenderer", *NAVIGATION_PLAYLIST_ID], True)
    service = nav(toplevel, [1, "buttonRenderer", "defaultServiceEndpoint"], True)
    if service:
        album["likeStatus"] = parse_like_status(service)

    return album


def parse_album_header_2024(response: JsonDict) -> JsonDict:
    header = nav(response, [*TWO_COLUMN_RENDERER, *TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
    album = {
        "title": nav(header, TITLE_TEXT),
        "type": nav(header, SUBTITLE),
        "thumbnails": nav(header, THUMBNAILS),
        "isExplicit": nav(header, SUBTITLE_BADGE_LABEL, True) is not None,
    }

    album["description"] = nav(header, ["description", *DESCRIPTION_SHELF, *DESCRIPTION], True)

    album_info = parse_song_runs(header["subtitle"]["runs"][2:])
    album_info["artists"] = [author] if (author := parse_base_header(header)["author"]) else None
    album.update(album_info)

    if len(header["secondSubtitle"]["runs"]) > 1:
        album["trackCount"] = to_int(header["secondSubtitle"]["runs"][0]["text"])
        album["duration"] = header["secondSubtitle"]["runs"][2]["text"]
    else:
        album["duration"] = header["secondSubtitle"]["runs"][0]["text"]

    # add to library/uploaded
    buttons = header["buttons"]
    album["audioPlaylistId"] = nav(
        find_object_by_key(buttons, "musicPlayButtonRenderer"),
        ["musicPlayButtonRenderer", "playNavigationEndpoint", *WATCH_PID],
        True,
    )
    # remove this once A/B testing is finished and it is no longer covered
    if album["audioPlaylistId"] is None:
        album["audioPlaylistId"] = nav(
            find_object_by_key(buttons, "musicPlayButtonRenderer"),
            ["musicPlayButtonRenderer", "playNavigationEndpoint", *WATCH_PLAYLIST_ID],
            True,
        )
    service = nav(
        find_object_by_key(buttons, "toggleButtonRenderer"),
        ["toggleButtonRenderer", "defaultServiceEndpoint"],
        True,
    )
    album["likeStatus"] = "INDIFFERENT"
    if service:
        album["likeStatus"] = parse_like_status(service)

    return album


def parse_album_playlistid_if_exists(data: JsonDict | None) -> str | None:
    """the content of the data changes based on whether the user is authenticated or not"""
    return nav(data, WATCH_PID, True) or nav(data, WATCH_PLAYLIST_ID, True) if data else None
