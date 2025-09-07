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
    # Check for iOS format first (musicShelfRenderer with musicTwoColumnItemRenderer)
    ios_results = get_library_contents(response, MUSIC_SHELF)
    if ios_results is not None:
        # iOS format detected - convert to standard format
        albums = parse_albums_ios_compatible(ios_results["contents"])
        
        if "continuations" in ios_results:
            # iOS continuations use different structure
            parse_func: ParseFuncType = lambda contents: parse_albums_ios_compatible(contents)
            remaining_limit = None if limit is None else (limit - len(albums))
            albums.extend(
                get_continuations(ios_results, "musicShelfContinuation", remaining_limit, request_func, parse_func)
            )
        
        return albums
    
    # Standard format (gridRenderer with musicTwoRowItemRenderer)
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


def parse_albums_ios_compatible(contents: JsonList) -> JsonList:
    """Parse albums from iOS format (musicTwoColumnItemRenderer) and convert to standard format"""
    albums = []
    
    for item in contents:
        if "musicTwoColumnItemRenderer" in item:
            ios_data = item["musicTwoColumnItemRenderer"]
            
            # Convert iOS format to standard musicTwoRowItemRenderer-like structure
            converted_data = {
                "title": ios_data.get("title", {}),
                "subtitle": ios_data.get("subtitle", {}),
                "navigationEndpoint": ios_data.get("navigationEndpoint", {}),
                "thumbnail": ios_data.get("thumbnail", {}),
                "menu": ios_data.get("menu", {})
            }
            
            # Create standard format wrapper
            standard_item = {MTRIR: converted_data}
            album = {}
            
            # Extract basic info
            album["browseId"] = nav(converted_data, TITLE + NAVIGATION_BROWSE_ID, True) or nav(converted_data, NAVIGATION_BROWSE_ID, True)
            album["title"] = nav(converted_data, TITLE_TEXT, True)
            
            # Extract thumbnail from iOS structure
            album["thumbnails"] = nav(converted_data, ["thumbnail", "musicThumbnailRenderer", "thumbnail", "thumbnails"], True)
            if not album["thumbnails"]:
                album["thumbnails"] = nav(converted_data, THUMBNAIL_RENDERER, True)
            
            # Extract playlist ID from menu (iOS format uses different structure)
            album["playlistId"] = None
            menu_items = nav(converted_data, MENU_ITEMS, True)
            if menu_items:
                # Try standard format first
                album["playlistId"] = nav(converted_data, MENU_PLAYLIST_ID, none_if_absent=True)
                
                # If not found, try iOS format (menuServiceItemRenderer with queueAddEndpoint)
                if not album["playlistId"]:
                    for item in menu_items:
                        if "menuServiceItemRenderer" in item:
                            service_endpoint = item["menuServiceItemRenderer"].get("serviceEndpoint", {})
                            queue_endpoint = service_endpoint.get("queueAddEndpoint", {})
                            queue_target = queue_endpoint.get("queueTarget", {})
                            playlist_id = queue_target.get("playlistId")
                            if playlist_id:
                                album["playlistId"] = playlist_id
                                break
            
            # Parse subtitle for type, artist, year
            if "runs" in converted_data.get("subtitle", {}):
                album["type"] = nav(converted_data, SUBTITLE, True)
                # Parse artist and year from subtitle runs (skip first 2 runs which are type and separator)
                if len(converted_data["subtitle"]["runs"]) > 2:
                    album.update(parse_song_runs(converted_data["subtitle"]["runs"][2:]))
            
            albums.append(album)
    
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
        # Try alternative path for iOS format
        results = get_library_contents(response, MUSIC_SHELF)
        if results is None:
            return []
        
        # iOS format - use artists parsing since podcasts might use similar structure
        podcasts = parse_podcasts_ios_compatible(results["contents"])
        
        if "continuations" in results:
            # iOS format continuation handling (similar to artists)
            if results["continuations"] and "nextContinuationData" in results["continuations"][0]:
                print("Note: iOS podcast format continuation available - implementing basic support")
                
                ios_continuation = results["continuations"][0]["nextContinuationData"]
                continuation_token = ios_continuation.get("continuation")
                
                if continuation_token:
                    try:
                        continuation_params = f"&ctoken={continuation_token}&continuation={continuation_token}"
                        continuation_response = request_func(continuation_params)
                        
                        if continuation_response and "continuationContents" in continuation_response:
                            continuation_contents = continuation_response["continuationContents"]
                            
                            if "sectionListContinuation" in continuation_contents:
                                section_continuation = continuation_contents["sectionListContinuation"]
                                
                                if "contents" in section_continuation:
                                    sections = section_continuation["contents"]
                                    
                                    for section in sections:
                                        if "musicShelfRenderer" in section:
                                            shelf = section["musicShelfRenderer"]
                                            shelf_contents = shelf.get("contents", [])
                                            
                                            continuation_podcasts = parse_podcasts_ios_compatible(shelf_contents)
                                            podcasts.extend(continuation_podcasts)
                                            print(f"✅ Added {len(continuation_podcasts)} podcasts from continuation")
                                            break
                    except Exception as e:
                        print(f"iOS podcast continuation error: {e}")
            else:
                # Standard continuation handling
                parse_func: ParseFuncType = lambda contents: parse_podcasts_ios_compatible(contents)
                remaining_limit = None if limit is None else (limit - len(podcasts))
                podcasts.extend(
                    get_continuations(results, "musicShelfContinuation", remaining_limit, request_func, parse_func)
                )
        
        return podcasts
    
    # Standard grid format
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
    
    # Check for iOS format (musicTwoColumnItemRenderer)
    artists = parse_artists_ios_compatible(results["contents"])

    if "continuations" in results:
        # Determine continuation type based on what's available
        if results["continuations"] and "nextContinuationData" in results["continuations"][0]:
            # iOS format uses nextContinuationData - implement basic support
            print("Note: iOS format continuation available - implementing basic support")
            
            ios_continuation = results["continuations"][0]["nextContinuationData"]
            continuation_token = ios_continuation.get("continuation")
            
            if continuation_token:
                try:
                    # Make continuation request using the proper format
                    # Format the continuation token as expected by _send_request
                    continuation_params = f"&ctoken={continuation_token}&continuation={continuation_token}"
                    continuation_response = request_func(continuation_params)
                    
                    # Parse iOS continuation response
                    if continuation_response and "continuationContents" in continuation_response:
                        continuation_contents = continuation_response["continuationContents"]
                        
                        # iOS continuation uses sectionListContinuation
                        if "sectionListContinuation" in continuation_contents:
                            section_continuation = continuation_contents["sectionListContinuation"]
                            
                            if "contents" in section_continuation:
                                sections = section_continuation["contents"]
                                
                                for section in sections:
                                    if "musicShelfRenderer" in section:
                                        shelf = section["musicShelfRenderer"]
                                        shelf_contents = shelf.get("contents", [])
                                        
                                        # Parse continuation items
                                        continuation_artists = parse_artists_ios_compatible(shelf_contents)
                                        artists.extend(continuation_artists)
                                        print(f"✅ Added {len(continuation_artists)} artists from continuation")
                                        break
                except Exception as e:
                    print(f"iOS continuation error: {e}")
        else:
            # Standard continuation handling
            parse_func: ParseFuncType = lambda contents: parse_artists_ios_compatible(contents)
            remaining_limit = None if limit is None else (limit - len(artists))
            artists.extend(
                get_continuations(results, "musicShelfContinuation", remaining_limit, request_func, parse_func)
            )

    return artists


def parse_podcasts_ios_compatible(contents: JsonList) -> JsonList:
    """Parse podcasts from iOS format (musicTwoColumnItemRenderer) and convert to standard format"""
    podcasts = []
    
    for result in contents:
        if "musicTwoColumnItemRenderer" in result:
            ios_data = result["musicTwoColumnItemRenderer"]
            
            # Convert to standard format for podcast parsing
            podcast = {}
            
            # Extract podcast title from title
            podcast["title"] = nav(ios_data, TITLE_TEXT, True)
            
            # Extract browse ID for podcast
            podcast["browseId"] = nav(ios_data, NAVIGATION_BROWSE_ID, True)
            
            # Extract podcast ID from browse ID (remove browse prefix)
            browse_id = podcast.get("browseId", "")
            if browse_id.startswith("MPSP"):
                # Extract playlist ID portion
                podcast["podcastId"] = browse_id.replace("MPSP", "")
            else:
                podcast["podcastId"] = browse_id
            
            # Extract channel information from subtitle
            subtitle_runs = nav(ios_data, ["subtitle", "runs"], True)
            if subtitle_runs and len(subtitle_runs) > 0:
                # Extract channel name
                channel_name = nav(subtitle_runs[0], "text", True)
                
                # Try to extract channel ID from navigation endpoint
                channel_id = None
                if "navigationEndpoint" in subtitle_runs[0]:
                    channel_id = nav(subtitle_runs[0], NAVIGATION_BROWSE_ID, True)
                
                podcast["channel"] = {
                    "name": channel_name,
                    "id": channel_id
                }
            else:
                podcast["channel"] = {
                    "name": None,
                    "id": None
                }
            
            # Extract thumbnails from iOS structure
            podcast["thumbnails"] = nav(ios_data, ["thumbnail", "musicThumbnailRenderer", "thumbnail", "thumbnails"], True)
            if not podcast["thumbnails"]:
                podcast["thumbnails"] = nav(ios_data, THUMBNAILS, True)
            
            podcasts.append(podcast)
        
        elif MRLIR in result:
            # Standard format - use existing parser
            podcasts.extend(parse_content_list([result], parse_podcast))
    
    return podcasts


def parse_artists_ios_compatible(contents: JsonList, uploaded: bool = False) -> JsonList:
    """Parse artists from iOS format (musicTwoColumnItemRenderer) and convert to standard format"""
    artists = []
    
    for result in contents:
        if "musicTwoColumnItemRenderer" in result:
            ios_data = result["musicTwoColumnItemRenderer"]
            
            # Convert to standard format for existing parser logic
            artist = {}
            
            # Extract browse ID
            artist["browseId"] = nav(ios_data, NAVIGATION_BROWSE_ID, True)
            
            # Extract artist name from title
            artist["artist"] = nav(ios_data, TITLE_TEXT, True)
            
            # Check page type from navigation endpoint
            page_type = nav(ios_data, NAVIGATION_BROWSE + PAGE_TYPE, True)
            if page_type == "MUSIC_PAGE_TYPE_USER_CHANNEL":
                artist["type"] = "channel"
            elif page_type == "MUSIC_PAGE_TYPE_ARTIST" or page_type == "MUSIC_PAGE_TYPE_LIBRARY_ARTIST":
                artist["type"] = "artist"
            
            # Parse menu playlists if available
            parse_menu_playlists(ios_data, artist)
            
            # Extract subscriber/song count from subtitle
            if uploaded:
                subtitle = nav(ios_data, ["subtitle", "runs", 0, "text"], True)
                if subtitle:
                    artist["songs"] = subtitle.split(" ")[0]
            else:
                subtitle = nav(ios_data, ["subtitle", "runs", 0, "text"], True)
                if subtitle:
                    # For artists, this could be subscriber count or song count
                    if "subscriber" in subtitle.lower():
                        artist["subscribers"] = subtitle.split(" ")[0]
                    elif "song" in subtitle.lower():
                        # Some artists show song count instead of subscribers
                        artist["songs"] = subtitle.split(" ")[0]
            
            # Extract thumbnails from iOS structure
            artist["thumbnails"] = nav(ios_data, ["thumbnail", "musicThumbnailRenderer", "thumbnail", "thumbnails"], True)
            if not artist["thumbnails"]:
                artist["thumbnails"] = nav(ios_data, THUMBNAILS, True)
            
            artists.append(artist)
        
        elif MRLIR in result:
            # Standard format - use existing parser
            artists.extend(parse_artists([result], uploaded))
    
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
