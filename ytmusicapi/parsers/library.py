from ytmusicapi.continuations import get_continuations
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType

from ._utils import *
from .browsing import parse_content_list
from .playlists import parse_playlist_items
from .podcasts import parse_podcast
from .songs import parse_song_runs


def parse_artists(results: JsonList, uploaded: bool = False) -> JsonList:
    artists = []
    for result in results:
        data = result[MRLIR]
        artist = {}
        artist["browseId"] = nav(data, NAVIGATION_BROWSE_ID)
        artist["artist"] = get_item_text(data, 0)
        page_type = nav(data, NAVIGATION_BROWSE + PAGE_TYPE, True)
        if page_type == "MUSIC_PAGE_TYPE_USER_CHANNEL":
            artist["type"] = "channel"
        elif page_type == "MUSIC_PAGE_TYPE_ARTIST":
            artist["type"] = "artist"
        parse_menu_playlists(data, artist)
        if uploaded:
            artist["songs"] = (get_item_text(data, 1) or "").split(" ")[0]
        else:
            subtitle = get_item_text(data, 1)
            if subtitle:
                artist["subscribers"] = subtitle.split(" ")[0]
        artist["thumbnails"] = nav(data, THUMBNAILS, True)
        artists.append(artist)

    return artists


def parse_library_albums(response: JsonDict, request_func: RequestFuncType, limit: int | None) -> JsonList:
    results = get_library_contents(response, GRID)
    if results is None:
        return []
    albums = parse_albums(results["items"])

    if "continuations" in results:
        parse_func: ParseFuncType = lambda contents: parse_albums(contents)
        remaining_limit = None if limit is None else (limit - len(albums))
        albums.extend(
            get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_func)
        )

    return albums


def parse_albums(results: JsonList) -> JsonList:
    albums = []
    for result in results:
        data = result[MTRIR]
        album = {}
        album["browseId"] = nav(data, TITLE + NAVIGATION_BROWSE_ID)
        album["playlistId"] = nav(data, MENU_PLAYLIST_ID, none_if_absent=True)
        album["title"] = nav(data, TITLE_TEXT)
        album["thumbnails"] = nav(data, THUMBNAIL_RENDERER)

        if "runs" in data["subtitle"]:
            album["type"] = nav(data, SUBTITLE)
            album.update(parse_song_runs(data["subtitle"]["runs"][2:]))

        albums.append(album)

    return albums


def parse_library_podcasts(response: JsonDict, request_func: RequestFuncType, limit: int | None) -> JsonList:
    results = get_library_contents(response, GRID)
    if results is None:
        return []
    parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_podcast)
    podcasts = parse_func(results["items"][1:])  # skip first entry "Add podcast"

    if "continuations" in results:
        remaining_limit = None if limit is None else (limit - len(podcasts))
        podcasts.extend(
            get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_func)
        )

    return podcasts


def parse_library_artists(response: JsonDict, request_func: RequestFuncType, limit: int | None) -> JsonList:
    results = get_library_contents(response, MUSIC_SHELF)
    if results is None:
        return []
    artists = parse_artists(results["contents"])

    if "continuations" in results:
        parse_func: ParseFuncType = lambda contents: parse_artists(contents)
        remaining_limit = None if limit is None else (limit - len(artists))
        artists.extend(
            get_continuations(results, "musicShelfContinuation", remaining_limit, request_func, parse_func)
        )

    return artists


def pop_songs_random_mix(results: JsonDict | None) -> None:
    """remove the random mix that conditionally appears at the start of library songs"""
    if results:
        if len(results["contents"]) >= 2:
            results["contents"].pop(0)


def parse_library_songs(response: JsonDict) -> JsonDict:
    results = get_library_contents(response, MUSIC_SHELF)
    pop_songs_random_mix(results)
    return {"results": results, "parsed": parse_playlist_items(results["contents"]) if results else results}


def get_library_contents(response: JsonDict, renderer: list[str]) -> JsonDict | None:
    """
    Find library contents. This function is a bit messy now
    as it is supporting two different response types. Can be
    cleaned up once all users are migrated to the new responses.
    :param response: ytmusicapi response
    :param renderer: GRID or MUSIC_SHELF
    :return: library contents or None
    """
    section = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST, True)
    if section is None:  # empty library or uploads
        # covers the case of non-premium subscribers - no downloads tab
        num_tabs = len(nav(response, [*SINGLE_COLUMN, "tabs"]))
        LIBRARY_TAB = TAB_1_CONTENT if num_tabs < 3 else TAB_2_CONTENT
        contents = nav(response, SINGLE_COLUMN + LIBRARY_TAB + SECTION_LIST_ITEM + renderer, True)
    else:
        results = find_object_by_key(section, "itemSectionRenderer")
        if results is None:
            contents = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + renderer, True)
        else:
            contents = nav(results, ITEM_SECTION + renderer, True)
    return contents
