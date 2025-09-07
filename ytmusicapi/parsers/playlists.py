import re

from ytmusicapi.continuations import *
from ytmusicapi.helpers import sum_total_duration
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncBodyType

from ..helpers import to_int
from .songs import *


def parse_playlist_header(response: JsonDict) -> JsonDict:
    playlist: JsonDict = {}
    editable_header = nav(response, [*HEADER, *EDITABLE_PLAYLIST_DETAIL_HEADER], True)
    playlist["owned"] = editable_header is not None
    playlist["privacy"] = "PUBLIC"
    if editable_header is not None:  # owned playlist
        header = nav(editable_header, HEADER_DETAIL)
        playlist["privacy"] = editable_header["editHeader"]["musicPlaylistEditHeaderRenderer"]["privacy"]
    else:
        header = nav(response, HEADER_DETAIL, True)
        if header is None:
            header = nav(
                response, [*TWO_COLUMN_RENDERER, *TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER]
            )

    playlist.update(parse_playlist_header_meta(header))
    if playlist["thumbnails"] is None:
        playlist["thumbnails"] = nav(header, THUMBNAIL_CROPPED, True)
    playlist["description"] = nav(header, ["description", *DESCRIPTION_SHELF, *DESCRIPTION], True)
    playlist["year"] = nav(header, SUBTITLE2)

    return playlist


def parse_playlist_header_meta(header: JsonDict) -> JsonDict:
    playlist_meta = {
        "views": None,
        "duration": None,
        "trackCount": None,
        "title": "".join([run["text"] for run in header.get("title", {}).get("runs", [])]),
        "thumbnails": nav(header, THUMBNAILS),
    }
    if "facepile" in header:
        playlist_meta["author"] = {
            "name": nav(header, ["facepile", "avatarStackViewModel", "text", "content"]),
            "id": nav(
                header,
                [
                    "facepile",
                    "avatarStackViewModel",
                    "rendererContext",
                    "commandContext",
                    "onTap",
                    "innertubeCommand",
                    "browseEndpoint",
                    "browseId",
                ],
                True,
            ),
        }
    if "runs" in header["secondSubtitle"]:
        second_subtitle_runs = header["secondSubtitle"]["runs"]
        has_views = (len(second_subtitle_runs) > 3) * 2
        playlist_meta["views"] = None if not has_views else to_int(second_subtitle_runs[0]["text"])
        has_duration = (len(second_subtitle_runs) > 1) * 2
        playlist_meta["duration"] = (
            None if not has_duration else second_subtitle_runs[has_views + has_duration]["text"]
        )
        song_count_text = second_subtitle_runs[has_views + 0]["text"]
        song_count_search = re.findall(r"\d+", song_count_text)
        # extract the digits from the text, return 0 if no match
        playlist_meta["trackCount"] = (
            to_int("".join(song_count_search)) if song_count_search is not None else None
        )

    return playlist_meta


def parse_audio_playlist(
    response: JsonDict, limit: int | None, request_func: RequestFuncBodyType
) -> JsonDict:
    playlist: JsonDict = {
        "owned": False,
        "privacy": "PUBLIC",
        "description": None,
        "views": None,
        "duration": None,
        "tracks": [],
        "thumbnails": [],
        "related": [],
    }

    section_list = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION])
    content_data = nav(section_list, [*CONTENT, "musicPlaylistShelfRenderer"])

    playlist["id"] = nav(
        content_data, [*CONTENT, MRLIR, *PLAY_BUTTON, "playNavigationEndpoint", *WATCH_PLAYLIST_ID]
    )
    playlist["trackCount"] = nav(content_data, ["collapsedItemCount"])

    playlist["tracks"] = []
    if "contents" in content_data:
        playlist["tracks"] = parse_playlist_items(content_data["contents"])

        parse_func: ParseFuncType = lambda contents: parse_playlist_items(contents)
        playlist["tracks"].extend(get_continuations_2025(content_data, limit, request_func, parse_func))

    playlist["title"] = playlist["tracks"][0]["album"]["name"]

    playlist["duration_seconds"] = sum_total_duration(playlist)
    return playlist


def parse_playlist_items(
    results: JsonList, menu_entries: list[list[str]] | None = None, is_album: bool = False
) -> JsonList:
    songs = []
    for result in results:
        # Handle both standard and iOS formats
        if MRLIR in result:
            data = result[MRLIR]
            song = parse_playlist_item(data, menu_entries, is_album)
            if song:
                songs.append(song)
        elif "musicTwoColumnItemRenderer" in result:
            # Handle iOS format
            data = result["musicTwoColumnItemRenderer"]
            song = parse_playlist_item_ios(data, menu_entries, is_album)
            if song:
                songs.append(song)

    return songs


def parse_playlist_item(
    data: JsonDict, menu_entries: list[list[str]] | None = None, is_album: bool = False
) -> JsonDict | None:
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

    isAvailable = True
    if "musicItemRendererDisplayPolicy" in data:
        isAvailable = data["musicItemRendererDisplayPolicy"] != "MUSIC_ITEM_RENDERER_DISPLAY_POLICY_GREY_OUT"

    # For unavailable items and for album track lists indexes are preset,
    # because meaning of the flex column cannot be reliably found using navigationEndpoint
    use_preset_columns = True if isAvailable is False or is_album is True else None

    title_index = 0 if use_preset_columns else None
    artist_index = 1 if use_preset_columns else None
    album_index = 2 if use_preset_columns else None
    user_channel_indexes = []
    unrecognized_index = None

    for index in range(len(data["flexColumns"])):
        flex_column_item = get_flex_column_item(data, index)
        navigation_endpoint = nav(flex_column_item, [*TEXT_RUN, "navigationEndpoint"], True)

        if not navigation_endpoint:
            if nav(flex_column_item, TEXT_RUN_TEXT, True) is not None:
                unrecognized_index = index if unrecognized_index is None else unrecognized_index
            continue

        if "watchEndpoint" in navigation_endpoint:
            title_index = index
        elif "browseEndpoint" in navigation_endpoint:
            page_type = nav(
                navigation_endpoint,
                [
                    "browseEndpoint",
                    "browseEndpointContextSupportedConfigs",
                    "browseEndpointContextMusicConfig",
                    "pageType",
                ],
            )

            # MUSIC_PAGE_TYPE_ARTIST for regular songs, MUSIC_PAGE_TYPE_UNKNOWN for uploads
            if page_type == "MUSIC_PAGE_TYPE_ARTIST" or page_type == "MUSIC_PAGE_TYPE_UNKNOWN":
                artist_index = index
            elif page_type == "MUSIC_PAGE_TYPE_ALBUM":
                album_index = index
            elif page_type == "MUSIC_PAGE_TYPE_USER_CHANNEL":
                user_channel_indexes.append(index)
            # Non music videos, for example: podcast episodes
            elif page_type == "MUSIC_PAGE_TYPE_NON_MUSIC_AUDIO_TRACK_PAGE":
                title_index = index

    # Extra check for rare songs, where artist is non-clickable and does not have navigationEndpoint
    if artist_index is None and unrecognized_index is not None:
        artist_index = unrecognized_index

    # Extra check for non-song videos, last channel is treated as artist
    if artist_index is None and user_channel_indexes:
        artist_index = user_channel_indexes[-1]

    title = get_item_text(data, title_index) if title_index is not None else None
    if title == "Song deleted":
        return None

    artists = parse_song_artists(data, artist_index) if artist_index is not None else None

    album = parse_song_album(data, album_index) if album_index is not None else None

    views = get_item_text(data, 2) if is_album else None

    duration = None
    if "fixedColumns" in data:
        if "simpleText" in nav(get_fixed_column_item(data, 0), ["text"]):
            duration = nav(get_fixed_column_item(data, 0), ["text", "simpleText"])
        else:
            duration = nav(get_fixed_column_item(data, 0), TEXT_RUN_TEXT)

    thumbnails = nav(data, THUMBNAILS, True)

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
        # sets the feedbackToken for get_history
        menu_items = nav(data, MENU_ITEMS)
        for menu_entry in menu_entries:
            items = find_objects_by_key(menu_items, menu_entry[0])
            song[menu_entry[-1]] = next(
                filter(lambda x: x is not None, (nav(itm, menu_entry, True) for itm in items)), None
            )

    return song


def parse_playlist_item_ios(
    data: JsonDict, menu_entries: list[list[str]] | None = None, is_album: bool = False
) -> JsonDict | None:
    """Parse playlist item in iOS format (musicTwoColumnItemRenderer)"""
    videoId = setVideoId = None
    like = None
    feedback_tokens = None
    library_status = None

    # Extract videoId from navigationEndpoint
    if "navigationEndpoint" in data and "watchEndpoint" in data["navigationEndpoint"]:
        videoId = data["navigationEndpoint"]["watchEndpoint"]["videoId"]
        
        # Extract playlistSetVideoId if available
        if "playlistSetVideoId" in data["navigationEndpoint"]["watchEndpoint"]:
            setVideoId = data["navigationEndpoint"]["watchEndpoint"]["playlistSetVideoId"]

    # Extract menu information if available
    if "menu" in data:
        for item in nav(data, MENU_ITEMS):
            if "menuServiceItemRenderer" in item:
                menu_service = nav(item, MENU_SERVICE)
                if "playlistEditEndpoint" in menu_service:
                    setVideoId = nav(menu_service, ["playlistEditEndpoint", "actions", 0, "setVideoId"], True)
                    if not videoId:  # fallback if not found above
                        videoId = nav(
                            menu_service, ["playlistEditEndpoint", "actions", 0, "removedVideoId"], True
                        )

            if TOGGLE_MENU in item:
                feedback_tokens = parse_song_menu_tokens(item)
                library_status = parse_song_library_status(item)

        # Check for like status in menu
        like = nav(data, MENU_LIKE_STATUS, True)

    # Extract title
    title = None
    if "title" in data and "runs" in data["title"] and len(data["title"]["runs"]) > 0:
        title = data["title"]["runs"][0]["text"]

    if title == "Song deleted":
        return None

    # Extract artists and duration from subtitle
    artists = None
    duration = None
    if "subtitle" in data and "runs" in data["subtitle"]:
        subtitle_runs = data["subtitle"]["runs"]
        if len(subtitle_runs) > 0:
            # First run is typically the artist
            artist_text = subtitle_runs[0]["text"]
            artists = [{"name": artist_text, "id": None}]
            
            # Look for duration (typically the last run after " • ")
            for run in subtitle_runs:
                text = run["text"]
                if ":" in text and (text.count(":") == 1 or text.count(":") == 2):
                    duration = text
                    break

    # Extract thumbnails
    thumbnails = None
    if "thumbnail" in data:
        thumbnails = nav(data, THUMBNAILS, True)

    # Assume available for iOS format items
    isAvailable = True
    isExplicit = False  # Would need to check badges if implemented

    # Default values for iOS format
    album = None
    views = None
    videoType = None

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
        song["trackNumber"] = None  # iOS format doesn't typically have track numbers

    if duration:
        song["duration"] = duration
        song["duration_seconds"] = parse_duration(duration)
    if setVideoId:
        song["setVideoId"] = setVideoId
    if feedback_tokens:
        song["feedbackTokens"] = feedback_tokens

    if menu_entries and "menu" in data:
        # sets the feedbackToken for get_history
        menu_items = nav(data, MENU_ITEMS)
        for menu_entry in menu_entries:
            items = find_objects_by_key(menu_items, menu_entry[0])
            song[menu_entry[-1]] = next(
                filter(lambda x: x is not None, (nav(itm, menu_entry, True) for itm in items)), None
            )

    return song


def validate_playlist_id(playlistId: str) -> str:
    return playlistId if not playlistId.startswith("VL") else playlistId[2:]
