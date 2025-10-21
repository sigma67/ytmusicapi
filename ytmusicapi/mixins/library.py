from collections.abc import Callable
import json
from random import randint

from requests import Response

from ytmusicapi.continuations import *
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.navigation import MUSIC_SHELF
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.library import *
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncDictType, ParseFuncType, RequestFuncType

from ..exceptions import YTMusicServerError
from ._protocol import MixinProtocol
from ._utils import *


class LibraryMixin(MixinProtocol):
    def get_library_playlists(self, limit: int | None = 25) -> JsonList:
        """
        Retrieves the playlists in the user's library.

        :param limit: Number of playlists to retrieve. ``None`` retrieves them all.
        :return: List of owned playlists.

        Each item is in the following format::

            {
                'playlistId': 'PLQwVIlKxHM6rz0fDJVv_0UlXGEWf-bFys',
                'title': 'Playlist title',
                'thumbnails: [...],
                'count': 5
            }
        """
        self._check_auth()
        body = {"browseId": "FEmusic_liked_playlists"}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        # Custom iOS-compatible navigation for library playlists
        results = None
        
        # Try standard paths first
        results = get_library_contents(response, GRID)
        if results is None:
            results = get_library_contents(response, MUSIC_SHELF)
        
        # If standard paths fail, try direct iOS path
        if results is None:
            try:
                # iOS format: contents.singleColumnBrowseResultsRenderer.tabs[0].tabRenderer.content.sectionListRenderer.contents[0].musicShelfRenderer
                contents = response.get("contents", {})
                scbr = contents.get("singleColumnBrowseResultsRenderer", {})
                tabs = scbr.get("tabs", [])
                if tabs:
                    tab_renderer = tabs[0].get("tabRenderer", {})
                    content = tab_renderer.get("content", {})
                    slr = content.get("sectionListRenderer", {})
                    sections = slr.get("contents", [])
                    
                    # Look for musicShelfRenderer in the first section
                    if sections and "musicShelfRenderer" in sections[0]:
                        results = sections[0]["musicShelfRenderer"]
            except (KeyError, IndexError):
                pass
        
        if results is None:
            return []
        
        # Handle different item structures between formats
        items = results.get("items", []) if isinstance(results, dict) else []
        
        # iOS format uses "contents" instead of "items"
        if not items and isinstance(results, dict):
            items = results.get("contents", [])
        if not items:
            return []
            
        if "musicTwoColumnItemRenderer" in str(items[0]):
            # iOS format uses musicTwoColumnItemRenderer, convert to regular format
            converted_items = []
            for item in items:
                if "musicTwoColumnItemRenderer" in item:
                    ios_item = item["musicTwoColumnItemRenderer"]
                    # Wrap in the expected musicTwoRowItemRenderer structure
                    converted_item = {
                        "musicTwoRowItemRenderer": {
                            "title": ios_item.get("title", {}),
                            "subtitle": ios_item.get("subtitle", {}),
                            "navigationEndpoint": ios_item.get("navigationEndpoint", {}),
                            "thumbnailRenderer": ios_item.get("thumbnail", {})
                        }
                    }
                    converted_items.append(converted_item)
                else:
                    converted_items.append(item)
            playlists = parse_content_list(converted_items, parse_playlist)
        else:
            # Traditional format, skip first item which is usually a header
            playlists = parse_content_list(items[1:], parse_playlist)

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_playlist)
            remaining_limit = None if limit is None else (limit - len(playlists))
            
            # Check for iOS format continuation first
            if results["continuations"] and "nextContinuationData" in results["continuations"][0]:
                # iOS format uses nextContinuationData - implement custom handling
                print("Note: iOS format continuation available for playlists")
                
                ios_continuation = results["continuations"][0]["nextContinuationData"]
                continuation_token = ios_continuation.get("continuation")
                
                if continuation_token:
                    try:
                        # Create continuation request body
                        continuation_body = dict(body)  # Copy original body
                        continuation_body["continuation"] = continuation_token
                        
                        continuation_response = self._send_request(endpoint, continuation_body)
                        
                        # Parse continuation response - iOS format uses different structure
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
                                            
                                            if shelf_contents:
                                                # Parse continuation items
                                                continuation_playlists = parse_func(shelf_contents)
                                                playlists.extend(continuation_playlists)
                                                print(f"✅ Added {len(continuation_playlists)} playlists from continuation")
                    except Exception as e:
                        print(f"⚠️ iOS continuation failed: {e}")
            else:
                # Desktop format uses gridContinuation
                playlists.extend(
                    get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_func)
                )

        return playlists

    def get_library_songs(
        self, limit: int = 25, validate_responses: bool = False, order: LibraryOrderType | None = None
    ) -> JsonList:
        """
        Gets the songs in the user's library (liked videos are not included).
        To get liked songs and videos, use :py:func:`get_liked_songs`

        :param limit: Number of songs to retrieve
        :param validate_responses: Flag indicating if responses from YTM should be validated and retried in case
            when some songs are missing. Default: False
        :param order: Order of songs to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of songs. Same format as :py:func:`get_playlist`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_liked_videos"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        per_page = 25

        request_func: RequestFuncType = lambda additionalParams: self._send_request(endpoint, body)
        
        # Custom iOS-compatible parser function
        def parse_func_ios_compatible(raw_response: JsonDict) -> JsonDict:
            response = raw_response
            
            # First check if this is iOS format by looking for musicTwoColumnItemRenderer
            response_str = json.dumps(response)
            is_ios_format = "musicTwoColumnItemRenderer" in response_str and "musicResponsiveListItemRenderer" not in response_str
            
            if is_ios_format:
                # Handle iOS format directly
                try:
                    contents = response.get("contents", {})
                    scbr = contents.get("singleColumnBrowseResultsRenderer", {})
                    tabs = scbr.get("tabs", [])
                    if tabs:
                        tab_renderer = tabs[0].get("tabRenderer", {})
                        content = tab_renderer.get("content", {})
                        slr = content.get("sectionListRenderer", {})
                        sections = slr.get("contents", [])
                        
                        if sections and "musicShelfRenderer" in sections[0]:
                            results = sections[0]["musicShelfRenderer"]
                            
                            # Remove unwanted items (if any)
                            pop_songs_random_mix(results)
                            
                            # Handle iOS format conversion
                            items = results.get("contents", [])
                            if items and "musicTwoColumnItemRenderer" in items[0]:
                                # Convert iOS format to regular format
                                converted_items = []
                                for item in items:
                                    if "musicTwoColumnItemRenderer" in item:
                                        ios_item = item["musicTwoColumnItemRenderer"]
                                        
                                        navigation_endpoint = ios_item.get("navigationEndpoint", {})
                                        
                                        # Extract title from iOS format
                                        title_text = None
                                        if "title" in ios_item and "runs" in ios_item["title"]:
                                            title_text = ios_item["title"]["runs"][0]["text"]
                                        
                                        # Extract artist and duration from subtitle (first run is artist, last part after • is duration)
                                        artist_text = None
                                        album_browse_id = None
                                        artist_browse_id = None
                                        
                                        if "subtitle" in ios_item and "runs" in ios_item["subtitle"]:
                                            # Parse subtitle - format is usually "Artist • Duration" or "Artist"
                                            subtitle_runs = ios_item["subtitle"]["runs"]
                                            if subtitle_runs:
                                                # First run is usually the artist
                                                artist_text = subtitle_runs[0]["text"]
                                                
                                                # Look for navigation endpoint to artist in subtitle runs
                                                for run in subtitle_runs:
                                                    if "navigationEndpoint" in run and "browseEndpoint" in run["navigationEndpoint"]:
                                                        browse_id = run["navigationEndpoint"]["browseEndpoint"].get("browseId", "")
                                                        if browse_id.startswith("UC"):  # Artist channel ID starts with UC
                                                            artist_browse_id = browse_id
                                        
                                        # Extract videoId from navigation endpoint
                                        video_id = None
                                        if "watchEndpoint" in navigation_endpoint:
                                            video_id = navigation_endpoint["watchEndpoint"].get("videoId")
                                        
                                        # Extract album and artist IDs from menu items
                                        if "menu" in ios_item and "menuRenderer" in ios_item["menu"]:
                                            menu_items = ios_item["menu"]["menuRenderer"].get("items", [])
                                            for menu_item in menu_items:
                                                if "menuNavigationItemRenderer" in menu_item:
                                                    nav_item = menu_item["menuNavigationItemRenderer"]
                                                    if "navigationEndpoint" in nav_item and "browseEndpoint" in nav_item["navigationEndpoint"]:
                                                        browse_endpoint = nav_item["navigationEndpoint"]["browseEndpoint"]
                                                        browse_id = browse_endpoint.get("browseId", "")
                                                        
                                                        # Check for album page type
                                                        if "browseEndpointContextSupportedConfigs" in browse_endpoint:
                                                            config = browse_endpoint["browseEndpointContextSupportedConfigs"]
                                                            if "browseEndpointContextMusicConfig" in config:
                                                                page_type = config["browseEndpointContextMusicConfig"].get("pageType")
                                                                if page_type == "MUSIC_PAGE_TYPE_ALBUM":
                                                                    album_browse_id = browse_id
                                                                elif page_type == "MUSIC_PAGE_TYPE_ARTIST" and not artist_browse_id:
                                                                    artist_browse_id = browse_id
                                        
                                        # Create flexColumns structure similar to regular format
                                        flex_columns = []
                                        
                                        # First column: title with navigation endpoint for videoId
                                        if title_text:
                                            title_column = {
                                                "musicResponsiveListItemFlexColumnRenderer": {
                                                    "text": {
                                                        "runs": [{"text": title_text}]
                                                    },
                                                    "displayPriority": "MUSIC_RESPONSIVE_LIST_ITEM_FLEX_COLUMN_DISPLAY_PRIORITY_HIGH"
                                                }
                                            }
                                            # Add navigation endpoint to title for videoId extraction
                                            if navigation_endpoint:
                                                title_column["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"][0]["navigationEndpoint"] = navigation_endpoint
                                            
                                            flex_columns.append(title_column)
                                        
                                        # Second column: artist with potential navigation endpoint and album
                                        if artist_text:
                                            artist_runs = [{"text": artist_text}]
                                            
                                            # Add artist navigation endpoint if available
                                            if artist_browse_id:
                                                artist_runs[0]["navigationEndpoint"] = {
                                                    "browseEndpoint": {
                                                        "browseId": artist_browse_id,
                                                        "browseEndpointContextSupportedConfigs": {
                                                            "browseEndpointContextMusicConfig": {
                                                                "pageType": "MUSIC_PAGE_TYPE_ARTIST"
                                                            }
                                                        }
                                                    }
                                                }
                                            
                                            # Add album information if available
                                            if album_browse_id:
                                                # Add separator and album as additional runs
                                                artist_runs.extend([
                                                    {"text": " • "},
                                                    {
                                                        "text": "Album",  # We could extract actual album name from menu text if needed
                                                        "navigationEndpoint": {
                                                            "browseEndpoint": {
                                                                "browseId": album_browse_id,
                                                                "browseEndpointContextSupportedConfigs": {
                                                                    "browseEndpointContextMusicConfig": {
                                                                        "pageType": "MUSIC_PAGE_TYPE_ALBUM"
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                ])
                                            
                                            artist_column = {
                                                "musicResponsiveListItemFlexColumnRenderer": {
                                                    "text": {
                                                        "runs": artist_runs
                                                    },
                                                    "displayPriority": "MUSIC_RESPONSIVE_LIST_ITEM_FLEX_COLUMN_DISPLAY_PRIORITY_HIGH"
                                                }
                                            }
                                            flex_columns.append(artist_column)
                                        
                                        converted_item = {
                                            "musicResponsiveListItemRenderer": {
                                                "flexColumns": flex_columns,
                                                "thumbnail": ios_item.get("thumbnail", {}),
                                                "menu": ios_item.get("menu", {}),
                                                "playNavigationEndpoint": navigation_endpoint,
                                                "navigationEndpoint": navigation_endpoint,
                                                # Add overlay structure for videoId extraction
                                                "overlay": {
                                                    "musicItemThumbnailOverlayRenderer": {
                                                        "content": {
                                                            "musicPlayButtonRenderer": {
                                                                "playNavigationEndpoint": navigation_endpoint
                                                            }
                                                        }
                                                    }
                                                } if navigation_endpoint else {}
                                            }
                                        }
                                        converted_items.append(converted_item)
                                    else:
                                        converted_items.append(item)
                                
                                # Update results with converted items
                                results = dict(results)  # Make a copy
                                results["contents"] = converted_items
                            
                            # Parse items
                            parsed_songs = parse_playlist_items(results["contents"]) if results else []
                            
                            return {"results": results, "parsed": parsed_songs}
                except (KeyError, IndexError) as e:
                    print(f"iOS parsing error: {e}")
                    return {"results": None, "parsed": None}
            
            # Try standard parsing for non-iOS format
            try:
                return parse_library_songs(raw_response)
            except Exception as e:
                print(f"Standard parsing error: {e}")
                return {"results": None, "parsed": None}

        if validate_responses and limit is None:
            raise YTMusicUserError("Validation is not supported without a limit parameter.")

        if validate_responses:
            validate_func: Callable[[JsonDict], bool] = lambda parsed: validate_response(
                parsed, per_page, limit, 0
            )
            response = resend_request_until_parsed_response_is_valid(
                request_func, "", parse_func_ios_compatible, validate_func, 3
            )
        else:
            response = parse_func_ios_compatible(request_func(""))

        results = response["results"]
        songs: JsonList | None = response["parsed"]
        if songs is None:
            return []

        if "continuations" in results:
            request_continuations_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_continuations_func = lambda contents: parse_playlist_items(contents)

            # Determine continuation type based on what's available
            if results["continuations"] and "nextContinuationData" in results["continuations"][0]:
                # iOS format uses nextContinuationData
                print("Note: iOS format continuation available - implementing basic support")
                
                # Basic iOS continuation handling
                ios_continuation = results["continuations"][0]["nextContinuationData"]
                continuation_token = ios_continuation.get("continuation")
                
                if continuation_token and not validate_responses:
                    # Make continuation request with proper format
                    try:
                        # Create continuation request body
                        continuation_body = dict(body)  # Copy original body
                        continuation_body["continuation"] = continuation_token
                        
                        continuation_response = self._send_request(endpoint, continuation_body)
                        
                        # Parse continuation response - iOS format uses different structure
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
                                            
                                            # Parse continuation items using the same iOS conversion logic
                                            if shelf_contents and "musicTwoColumnItemRenderer" in shelf_contents[0]:
                                                # Create a fake response structure for our parser
                                                fake_response = {
                                                    "contents": {
                                                        "singleColumnBrowseResultsRenderer": {
                                                            "tabs": [{
                                                                "tabRenderer": {
                                                                    "content": {
                                                                        "sectionListRenderer": {
                                                                            "contents": [{
                                                                                "musicShelfRenderer": {
                                                                                    "contents": shelf_contents
                                                                                }
                                                                            }]
                                                                        }
                                                                    }
                                                                }
                                                            }]
                                                        }
                                                    }
                                                }
                                                
                                                # Apply same iOS conversion logic
                                                continuation_parsed = parse_func_ios_compatible(fake_response)
                                                if continuation_parsed and continuation_parsed["parsed"]:
                                                    continuation_songs = continuation_parsed["parsed"]
                                                    songs.extend(continuation_songs)
                                                    print(f"✅ Added {len(continuation_songs)} songs from continuation")
                                                    
                                                    # Check for more continuations in this batch
                                                    if "continuations" in shelf:
                                                        print(f"📄 More continuations available ({len(shelf['continuations'])} batches)")
                                            break
                    except Exception as e:
                        print(f"iOS continuation error: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                # Standard continuation handling
                if validate_responses:
                    songs.extend(
                        get_validated_continuations(
                            results,
                            "musicShelfContinuation",
                            limit - len(songs),
                            per_page,
                            request_continuations_func,
                            parse_continuations_func,
                        )
                    )
                else:
                    remaining_limit = None if limit is None else (limit - len(songs))
                    songs.extend(
                        get_continuations(
                            results,
                            "musicShelfContinuation",
                            remaining_limit,
                            request_continuations_func,
                            parse_continuations_func,
                        )
                    )

        return songs

    def get_library_albums(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the albums in the user's library.

        :param limit: Number of albums to return
        :param order: Order of albums to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of albums.

        Each item is in the following format::

            {
              "browseId": "MPREb_G8AiyN7RvFg",
              "playlistId": "OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc",
              "title": "Beautiful",
              "type": "Album",
              "thumbnails": [...],
              "artists": [{
                "name": "Project 46",
                "id": "UCXFv36m62USAN5rnVct9B4g"
              }],
              "year": "2015"
            }
        """
        self._check_auth()
        body = {"browseId": "FEmusic_liked_albums"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)

        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_albums(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_artists(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the artists of the songs in the user's library.

        :param limit: Number of artists to return
        :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of artists.

        Each item is in the following format::

            {
              "browseId": "UCxEqaQWosMHaTih-tgzDqug",
              "artist": "WildVibes",
              "subscribers": "2.91K",
              "thumbnails": [...]
            }
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_corpus_track_artists"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_subscriptions(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the artists the user has subscribed to.

        :param limit: Number of artists to return
        :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of artists. Same format as :py:func:`get_library_artists`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_corpus_artists"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_podcasts(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Get podcasts the user has added to the library

        :param limit: Number of podcasts to return
        :param order: Order of podcasts to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of podcasts. New Episodes playlist is the first podcast returned, but only if subscribed to relevant podcasts.

        Example::

            [
                {
                    "title": "New Episodes",
                    "channel":
                    {
                        "id": null,
                        "name": "Auto playlist"
                    },
                    "browseId": "VLRDPN",
                    "podcastId": "RDPN",
                    "thumbnails": [...]
                },
                {
                    "title": "5 Minuten Harry Podcast",
                    "channel":
                    {
                        "id": "UCDIDXF4WM1qQzerrxeEfSdA",
                        "name": "coldmirror"
                    },
                    "browseId": "MPSPPLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH",
                    "podcastId": "PLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH",
                    "thumbnails": [...]
                }
            ]
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_non_music_audio_list"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_podcasts(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_channels(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Get channels the user has added to the library

        :param limit: Number of channels to return
        :param order: Order of channels to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of channels.

        Example::

            [
                {
                    "browseId": "UCRFF8xw5dg9mL4r5ryFOtKw",
                    "artist": "Jumpers Jump",
                    "subscribers": "1.54M",
                    "thumbnails": [...]
                },
                {
                    "browseId": "UCQ3f2_sO3NJyDkuCxCNSOVA",
                    "artist": "BROWN BAG",
                    "subscribers": "74.2K",
                    "thumbnails": [...]
                }
            ]
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_non_music_audio_channels_list"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_history(self) -> JsonList:
        """
        Gets your play history in reverse chronological order

        :return: List of playlistItems, see :py:func:`get_playlist`
          The additional property ``played`` indicates when the playlistItem was played
          The additional property ``feedbackToken`` can be used to remove items with :py:func:`remove_history_items`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_history"}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        songs = []
        for content in results:
            data = nav(content, [*MUSIC_SHELF, "contents"], True)
            if not data:
                error = nav(content, ["musicNotifierShelfRenderer", *TITLE], True)
                raise YTMusicServerError(error)
            menu_entries = [[*MENU_SERVICE, *FEEDBACK_TOKEN]]
            songlist = parse_playlist_items(data, menu_entries)
            for song in songlist:
                song["played"] = nav(content["musicShelfRenderer"], TITLE_TEXT)
            songs.extend(songlist)

        return songs

    def add_history_item(self, song: JsonDict) -> Response:
        """
        Add an item to the account's history using the playbackTracking URI
        obtained from :py:func:`get_song`. A ``204`` return code indicates success.

        Usage::

            song = yt_auth.get_song(videoId)
            response = yt_auth.add_history_item(song)

        .. note::

            You need to use the same YTMusic instance as you used for :py:func:`get_song`.

        :param song: Dictionary as returned by :py:func:`get_song`
        :return: Full response. response.status_code is 204 if successful
        """
        self._check_auth()
        url = song["playbackTracking"]["videostatsPlaybackUrl"]["baseUrl"]
        CPNA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        cpn = "".join(CPNA[randint(0, 256) & 63] for _ in range(0, 16))
        params = {"ver": 2, "c": "WEB_REMIX", "cpn": cpn}
        return self._send_get_request(url, params)

    def remove_history_items(self, feedbackTokens: list[str]) -> JsonDict:  # pragma: no cover
        """
        Remove an item from the account's history. This method does currently not work with brand accounts

        :param feedbackTokens: Token to identify the item to remove, obtained from :py:func:`get_history`
        :return: Full response
        """
        self._check_auth()
        body = {"feedbackTokens": feedbackTokens}
        endpoint = "feedback"
        response = self._send_request(endpoint, body)

        return response

    def rate_song(self, videoId: str, rating: LikeStatus = LikeStatus.INDIFFERENT) -> JsonDict | None:
        """
        Rates a song ("thumbs up"/"thumbs down" interactions on YouTube Music)

        :param videoId: Video id
        :param rating: One of ``LIKE``, ``DISLIKE``, ``INDIFFERENT``

          | ``INDIFFERENT`` removes the previous rating and assigns no rating

        :return: Full response
        :raises: YTMusicUserError if an invalid rating ir povided
        """
        self._check_auth()
        body = {"target": {"videoId": videoId}}
        endpoint = prepare_like_endpoint(rating)
        return self._send_request(endpoint, body)

    def edit_song_library_status(self, feedbackTokens: list[str] | None = None) -> JsonDict:
        """
        Adds or removes a song from your library depending on the token provided.

        :param feedbackTokens: List of feedbackTokens obtained from authenticated requests
            to endpoints that return songs (i.e. :py:func:`get_album`)
        :return: Full response
        """
        self._check_auth()
        body = {"feedbackTokens": feedbackTokens}
        endpoint = "feedback"
        return self._send_request(endpoint, body)

    def rate_playlist(self, playlistId: str, rating: LikeStatus = LikeStatus.INDIFFERENT) -> JsonDict:
        """
        Rates a playlist/album ("Add to library"/"Remove from library" interactions on YouTube Music)
        You can also dislike a playlist/album, which has an effect on your recommendations

        :param playlistId: Playlist id
        :param rating: One of ``LIKE``, ``DISLIKE``, ``INDIFFERENT``

          | ``INDIFFERENT`` removes the playlist/album from the library

        :return: Full response
        :raises: YTMusicUserError if an invalid rating is provided
        """
        self._check_auth()
        body = {"target": {"playlistId": playlistId}}
        endpoint = prepare_like_endpoint(rating)
        return self._send_request(endpoint, body)

    def subscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """
        Subscribe to artists. Adds the artists to your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {"channelIds": channelIds}
        endpoint = "subscription/subscribe"
        return self._send_request(endpoint, body)

    def unsubscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """
        Unsubscribe from artists. Removes the artists from your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {"channelIds": channelIds}
        endpoint = "subscription/unsubscribe"
        return self._send_request(endpoint, body)

    def get_account_info(self) -> JsonDict:
        """
        Gets information about the currently authenticated user's account.
        Compatible with both desktop and iOS mobile single-column formats.

        :return: Dictionary with user's account name, channel handle, and URL of their account photo.

        Example::

            {
                "accountName": "Sample User",
                "channelHandle": "@SampleUser
                "accountPhotoUrl": "https://yt3.ggpht.com/sample-user-photo"
            }
        """
        self._check_auth()
        endpoint = "account/account_menu"
        response = self._send_request(endpoint, {})

        # Try desktop navigation paths first (backward compatibility)
        try:
            ACCOUNT_INFO = [
                "actions",
                0,
                "openPopupAction",
                "popup",
                "multiPageMenuRenderer",
                "header",
                "activeAccountHeaderRenderer",
            ]
            ACCOUNT_RUNS_TEXT = ["runs", 0, "text"]
            ACCOUNT_NAME = [*ACCOUNT_INFO, "accountName", *ACCOUNT_RUNS_TEXT]
            ACCOUNT_CHANNEL_HANDLE = [*ACCOUNT_INFO, "channelHandle", *ACCOUNT_RUNS_TEXT]
            ACCOUNT_PHOTO_URL = [*ACCOUNT_INFO, "accountPhoto", "thumbnails", 0, "url"]

            account_name = nav(response, ACCOUNT_NAME)
            channel_handle = nav(response, ACCOUNT_CHANNEL_HANDLE, none_if_absent=True)
            account_photo_url = nav(response, ACCOUNT_PHOTO_URL)

            return {
                "accountName": account_name,
                "channelHandle": channel_handle,
                "accountPhotoUrl": account_photo_url,
            }
        except:
            # Fall back to iOS mobile navigation paths
            try:
                # iOS format typically omits 'openPopupAction' level
                IOS_ACCOUNT_INFO = [
                    "actions",
                    0,
                    "popup",
                    "multiPageMenuRenderer",
                    "header",
                    "activeAccountHeaderRenderer",
                ]
                ACCOUNT_RUNS_TEXT = ["runs", 0, "text"]
                IOS_ACCOUNT_NAME = [*IOS_ACCOUNT_INFO, "accountName", *ACCOUNT_RUNS_TEXT]
                IOS_ACCOUNT_CHANNEL_HANDLE = [*IOS_ACCOUNT_INFO, "channelHandle", *ACCOUNT_RUNS_TEXT]
                IOS_ACCOUNT_PHOTO_URL = [*IOS_ACCOUNT_INFO, "accountPhoto", "thumbnails", 0, "url"]

                account_name = nav(response, IOS_ACCOUNT_NAME)
                channel_handle = nav(response, IOS_ACCOUNT_CHANNEL_HANDLE, none_if_absent=True)
                account_photo_url = nav(response, IOS_ACCOUNT_PHOTO_URL)

                return {
                    "accountName": account_name,
                    "channelHandle": channel_handle,
                    "accountPhotoUrl": account_photo_url,
                }
            except:
                # Final fallback for alternative iOS structures
                try:
                    # Some iOS variants might have different action structure
                    ALT_IOS_HEADER = ["popup", "multiPageMenuRenderer", "header", "activeAccountHeaderRenderer"]
                    ALT_ACCOUNT_NAME = [*ALT_IOS_HEADER, "accountName", "runs", 0, "text"]
                    ALT_ACCOUNT_CHANNEL_HANDLE = [*ALT_IOS_HEADER, "channelHandle", "runs", 0, "text"]
                    ALT_ACCOUNT_PHOTO_URL = [*ALT_IOS_HEADER, "accountPhoto", "thumbnails", 0, "url"]

                    account_name = nav(response, ALT_ACCOUNT_NAME)
                    channel_handle = nav(response, ALT_ACCOUNT_CHANNEL_HANDLE, none_if_absent=True)
                    account_photo_url = nav(response, ALT_ACCOUNT_PHOTO_URL)

                    return {
                        "accountName": account_name,
                        "channelHandle": channel_handle,
                        "accountPhotoUrl": account_photo_url,
                    }
                except Exception as e:
                    # If all navigation attempts fail, raise informative error
                    raise Exception(f"Unable to parse account info from response. The response structure may have changed or be unsupported in this format. Original error: {e}")
