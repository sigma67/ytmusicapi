import re
import warnings
from typing import Literal, cast, overload

from ytmusicapi.continuations import (
    get_continuations,
    get_reloadable_continuation_params,
)
from ytmusicapi.helpers import YTM_DOMAIN, sum_total_duration
from ytmusicapi.models.lyrics import LyricLine, Lyrics, TimedLyrics
from ytmusicapi.parsers.albums import parse_album_header_2024
from ytmusicapi.parsers.browsing import (
    parse_album,
    parse_content_list,
    parse_mixed_content,
    parse_playlist,
    parse_video,
)
from ytmusicapi.parsers.library import parse_albums
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType

from ..exceptions import YTMusicError, YTMusicUserError
from ..navigation import *
from ._protocol import MixinProtocol
from ._utils import get_datestamp


class BrowsingMixin(MixinProtocol):
    def get_home(self, limit: int = 3) -> JsonList:
        """
        Get the home page.
        The home page is structured as titled rows, returning 3 rows of music suggestions at a time.
        Content varies and may contain artist, album, song or playlist suggestions, sometimes mixed within the same row

        :param limit: Number of rows on the home page to return
        :return: List of dictionaries keyed with 'title' text and 'contents' list

        Example list::

            [
                {
                    "title": "Your morning music",
                    "contents": [
                        { //album result
                            "title": "Sentiment",
                            "browseId": "MPREb_QtqXtd2xZMR",
                            "thumbnails": [...]
                        },
                        { //playlist result
                            "title": "r/EDM top submissions 01/28/2022",
                            "playlistId": "PLz7-xrYmULdSLRZGk-6GKUtaBZcgQNwel",
                            "thumbnails": [...],
                            "description": "redditEDM • 161 songs",
                            "count": "161",
                            "author": [
                                {
                                    "name": "redditEDM",
                                    "id": "UCaTrZ9tPiIGHrkCe5bxOGwA"
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": "Your favorites",
                    "contents": [
                        { //artist result
                            "title": "Chill Satellite",
                            "browseId": "UCrPLFBWdOroD57bkqPbZJog",
                            "subscribers": "374",
                            "thumbnails": [...]
                        }
                        { //album result
                            "title": "Dragon",
                            "year": "Two Steps From Hell",
                            "browseId": "MPREb_M9aDqLRbSeg",
                            "thumbnails": [...]
                        }
                    ]
                },
                {
                    "title": "Quick picks",
                    "contents": [
                        { //song quick pick
                            "title": "Gravity",
                            "videoId": "EludZd6lfts",
                            "artists": [{
                                    "name": "yetep",
                                    "id": "UCSW0r7dClqCoCvQeqXiZBlg"
                                }],
                            "thumbnails": [...],
                            "album": {
                                "name": "Gravity",
                                "id": "MPREb_D6bICFcuuRY"
                            }
                        },
                        { //video quick pick
                            "title": "Gryffin & Illenium (feat. Daya) - Feel Good (L3V3LS Remix)",
                            "videoId": "bR5l0hJDnX8",
                            "artists": [
                                {
                                    "name": "L3V3LS",
                                    "id": "UCCVNihbOdkOWw_-ajIYhAbQ"
                                }
                            ],
                            "thumbnails": [...],
                            "views": "10M"
                        }
                    ]
                }
            ]

        """
        endpoint = "browse"
        body = {"browseId": "FEmusic_home"}
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        
        # Check if we have iOS Music format (elementRenderer structure)
        if results and len(results) > 0 and 'elementRenderer' in results[0]:
            home = self._parse_ios_mixed_content(results)
        else:
            # Use traditional parsing for web format
            home = parse_mixed_content(results)

        section_list = nav(response, [*SINGLE_COLUMN_TAB, "sectionListRenderer"])
        if "continuations" in section_list:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )

            parse_func = self._parse_ios_mixed_content if (results and len(results) > 0 and 'elementRenderer' in results[0]) else parse_mixed_content

            home.extend(
                get_continuations(
                    section_list,
                    "sectionListContinuation",
                    limit - len(home),
                    request_func,
                    parse_func,
                )
            )

        return home

    def get_artist(self, channelId: str) -> JsonDict:
        """
        Get information about an artist and their top releases (songs,
        albums, singles, videos, and related artists). The top lists
        contain pointers for getting the full list of releases.

        Possible content types for get_artist are:

            - songs
            - albums
            - singles
            - shows
            - videos
            - episodes
            - podcasts
            - related

        Each of these content keys in the response contains
        ``results`` and possibly ``browseId`` and ``params``.

        - For songs/videos, pass the browseId to :py:func:`get_playlist`.
        - For albums/singles/shows, pass browseId and params to :py:func:`get_artist_albums`.

        :param channelId: channel id of the artist
        :return: Dictionary with requested information.

        .. warning::

            The returned channelId is not the same as the one passed to the function.
            It should be used only with :py:func:`subscribe_artists`.

        Example::

            {
                "description": "Oasis were ...",
                "views": "3,693,390,359 views",
                "name": "Oasis",
                "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q",
                "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg",
                "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg",
                "subscribers": "3.86M",
                "subscribed": false,
                "thumbnails": [...],
                "songs": {
                    "browseId": "VLPLMpM3Z0118S42R1npOhcjoakLIv1aqnS1",
                    "results": [
                        {
                            "videoId": "ZrOKjDZOtkA",
                            "title": "Wonderwall (Remastered)",
                            "thumbnails": [...],
                            "artist": "Oasis",
                            "album": "(What's The Story) Morning Glory? (Remastered)"
                        }
                    ]
                },
                "albums": {
                    "results": [
                        {
                            "title": "Familiar To Millions",
                            "thumbnails": [...],
                            "year": "2018",
                            "browseId": "MPREb_AYetWMZunqA"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "singles": {
                    "results": [
                        {
                            "title": "Stand By Me (Mustique Demo)",
                            "thumbnails": [...],
                            "year": "2016",
                            "browseId": "MPREb_7MPKLhibN5G"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "videos": {
                    "results": [
                        {
                            "title": "Wonderwall",
                            "thumbnails": [...],
                            "views": "358M",
                            "videoId": "bx1Bh8ZvH84",
                            "playlistId": "PLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                        }
                    ],
                    "browseId": "VLPLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                },
                "related": {
                    "results": [
                        {
                            "browseId": "UCt2KxZpY5D__kapeQ8cauQw",
                            "subscribers": "450K",
                            "title": "The Verve"
                        },
                        {
                            "browseId": "UCwK2Grm574W1u-sBzLikldQ",
                            "subscribers": "341K",
                            "title": "Liam Gallagher"
                        },
                        ...
                    ]
                }
            }
        """
        if channelId.startswith("MPLA"):
            channelId = channelId[4:]
        body = {"browseId": channelId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)

        artist: JsonDict = {"description": None, "views": None}
        
        # Handle both traditional and iOS header formats
        if "musicImmersiveHeaderRenderer" in response["header"]:
            # Traditional format
            header = response["header"]["musicImmersiveHeaderRenderer"]
        elif "musicVisualHeaderRenderer" in response["header"]:
            # iOS format
            header = response["header"]["musicVisualHeaderRenderer"]
        else:
            raise Exception(f"Unknown header format. Available keys: {list(response['header'].keys())}")
            
        artist["name"] = nav(header, TITLE_TEXT)
        descriptionShelf = find_object_by_key(results, DESCRIPTION_SHELF[0], is_key=True)
        if descriptionShelf:
            artist["description"] = nav(descriptionShelf, DESCRIPTION)
            artist["views"] = (
                None
                if "subheader" not in descriptionShelf
                else descriptionShelf["subheader"]["runs"][0]["text"]
            )
        subscription_button = header["subscriptionButton"]["subscribeButtonRenderer"]
        artist["channelId"] = subscription_button["channelId"]
        artist["shuffleId"] = nav(header, ["playButton", "buttonRenderer", *NAVIGATION_PLAYLIST_ID], True)
        artist["radioId"] = nav(header, ["startRadioButton", "buttonRenderer", *NAVIGATION_PLAYLIST_ID], True)
        artist["subscribers"] = nav(subscription_button, ["subscriberCountText", "runs", 0, "text"], True)
        artist["subscribed"] = subscription_button["subscribed"]
        artist["thumbnails"] = nav(header, THUMBNAILS, True)
        artist["songs"] = {"browseId": None}
        if "musicShelfRenderer" in results[0]:  # API sometimes does not return songs
            musicShelf = nav(results[0], MUSIC_SHELF)
            if "navigationEndpoint" in nav(musicShelf, TITLE):
                artist["songs"]["browseId"] = nav(musicShelf, TITLE + NAVIGATION_BROWSE_ID)
            artist["songs"]["results"] = parse_playlist_items(musicShelf["contents"])

        # Check if we have iOS format sections
        has_ios_sections = any(
            "itemSectionRenderer" in section and 
            "contents" in section["itemSectionRenderer"] and
            len(section["itemSectionRenderer"]["contents"]) > 0 and
            "elementRenderer" in section["itemSectionRenderer"]["contents"][0]
            for section in results
        )
        
        if has_ios_sections:
            # Parse iOS format sections
            artist.update(self._parse_ios_artist_sections(results))
        else:
            # Parse traditional format sections
            artist.update(self.parser.parse_channel_contents(results))
        
        return artist

    def _parse_ios_artist_sections(self, results):
        """Parse artist sections in iOS format (elementRenderer with musicListItemCarouselModel/musicGridItemCarouselModel)"""
        artist_sections = {}
        
        for section in results:
            if "itemSectionRenderer" in section:
                item_section = section["itemSectionRenderer"]
                if "contents" in item_section and item_section["contents"]:
                    content = item_section["contents"][0]
                    
                    if "elementRenderer" in content:
                        element = content["elementRenderer"]
                        if "newElement" in element and "type" in element["newElement"]:
                            new_elem = element["newElement"]
                            if "componentType" in new_elem["type"] and "model" in new_elem["type"]["componentType"]:
                                model = new_elem["type"]["componentType"]["model"]
                                
                                # Parse songs (musicListItemCarouselModel)
                                if "musicListItemCarouselModel" in model:
                                    carousel = model["musicListItemCarouselModel"]
                                    if "header" in carousel and "title" in carousel["header"]:
                                        title = carousel["header"]["title"].lower()
                                        if "song" in title or "top" in title:
                                            songs_data = self._parse_ios_songs_section(carousel)
                                            if songs_data:
                                                artist_sections["songs"] = songs_data
                                
                                # Parse albums/singles/videos (musicGridItemCarouselModel)
                                elif "musicGridItemCarouselModel" in model:
                                    carousel = model["musicGridItemCarouselModel"]
                                    # Check for header in shelf structure (iOS format)
                                    header_title = None
                                    if "shelf" in carousel and "header" in carousel["shelf"] and "title" in carousel["shelf"]["header"]:
                                        header_title = carousel["shelf"]["header"]["title"].lower()
                                    elif "header" in carousel and "title" in carousel["header"]:
                                        header_title = carousel["header"]["title"].lower()
                                    
                                    if header_title:
                                        section_data = self._parse_ios_grid_section(carousel)
                                        if section_data:
                                            if "album" in header_title:
                                                artist_sections["albums"] = section_data
                                            elif "single" in header_title or "ep" in header_title:
                                                artist_sections["singles"] = section_data
                                            elif "video" in header_title:
                                                artist_sections["videos"] = section_data
                                            elif "playlist" in header_title or "featured" in header_title:
                                                artist_sections["playlists"] = section_data
                                            elif "fan" in header_title or "might" in header_title or "like" in header_title:
                                                artist_sections["related"] = section_data
        
        return artist_sections
    
    def _parse_ios_songs_section(self, carousel):
        """Parse iOS songs section (musicListItemCarouselModel)"""
        section_data = {"browseId": None, "results": []}
        
        # Get browseId from header if available
        if "header" in carousel and "onTap" in carousel["header"]:
            on_tap = carousel["header"]["onTap"]
            if "innertubeCommand" in on_tap and "browseEndpoint" in on_tap["innertubeCommand"]:
                browse_endpoint = on_tap["innertubeCommand"]["browseEndpoint"]
                section_data["browseId"] = browse_endpoint.get("browseId")
        
        # Parse song items
        if "items" in carousel:
            for item in carousel["items"]:
                song = {}
                if "title" in item:
                    song["title"] = item["title"]
                if "subtitle" in item:
                    # Parse artist and play count from subtitle
                    subtitle = item["subtitle"]
                    if " • " in subtitle:
                        parts = subtitle.split(" • ")
                        song["artist"] = parts[0]
                        if len(parts) > 1:
                            song["playCount"] = parts[1]
                    else:
                        song["artist"] = subtitle
                        
                if "onTap" in item and "innertubeCommand" in item["onTap"]:
                    command = item["onTap"]["innertubeCommand"]
                    if "watchEndpoint" in command:
                        watch_endpoint = command["watchEndpoint"]
                        song["videoId"] = watch_endpoint.get("videoId")
                        song["playlistId"] = watch_endpoint.get("playlistId")
                        
                if "thumbnail" in item and "image" in item["thumbnail"]:
                    song["thumbnails"] = item["thumbnail"]["image"].get("sources", [])
                
                section_data["results"].append(song)
        
        return section_data
    
    def _parse_ios_grid_section(self, carousel):
        """Parse iOS grid section (musicGridItemCarouselModel)"""
        section_data = {"browseId": None, "results": []}
        
        # Get browseId from header (can be in shelf.header or direct header)
        if "shelf" in carousel and "header" in carousel["shelf"] and "onTap" in carousel["shelf"]["header"]:
            on_tap = carousel["shelf"]["header"]["onTap"]
            if "innertubeCommand" in on_tap and "browseEndpoint" in on_tap["innertubeCommand"]:
                browse_endpoint = on_tap["innertubeCommand"]["browseEndpoint"]
                section_data["browseId"] = browse_endpoint.get("browseId")
                if "params" in browse_endpoint:
                    section_data["params"] = browse_endpoint["params"]
        elif "header" in carousel and "onTap" in carousel["header"]:
            on_tap = carousel["header"]["onTap"]
            if "innertubeCommand" in on_tap and "browseEndpoint" in on_tap["innertubeCommand"]:
                browse_endpoint = on_tap["innertubeCommand"]["browseEndpoint"]
                section_data["browseId"] = browse_endpoint.get("browseId")
                if "params" in browse_endpoint:
                    section_data["params"] = browse_endpoint["params"]
        
        # Parse grid items (albums, singles, videos, etc.)
        # Items can be in 'items' or 'shelf.items'
        items = []
        if "items" in carousel:
            items = carousel["items"]
        elif "shelf" in carousel and "items" in carousel["shelf"]:
            items = carousel["shelf"]["items"]
            
        for item in items:
            grid_item = {}
            if "title" in item:
                grid_item["title"] = item["title"]
            if "subtitle" in item:
                grid_item["subtitle"] = item["subtitle"]
                    
            if "onTap" in item and "innertubeCommand" in item["onTap"]:
                command = item["onTap"]["innertubeCommand"]
                if "browseEndpoint" in command:
                    browse_endpoint = command["browseEndpoint"]
                    grid_item["browseId"] = browse_endpoint.get("browseId")
                elif "watchEndpoint" in command:
                    watch_endpoint = command["watchEndpoint"]
                    grid_item["videoId"] = watch_endpoint.get("videoId")
                    grid_item["playlistId"] = watch_endpoint.get("playlistId")
                    
            if "thumbnail" in item and "image" in item["thumbnail"]:
                grid_item["thumbnails"] = item["thumbnail"]["image"].get("sources", [])
            
            section_data["results"].append(grid_item)
        
        return section_data

    def _parse_ios_albums(self, contents):
        """Parse iOS format albums from gridRenderer items"""
        albums = []
        for result in contents:
            if "musicTwoRowItemRenderer" not in result:
                continue
                
            data = result["musicTwoRowItemRenderer"]
            album = {}
            
            # Get browseId from navigationEndpoint at root level (iOS format)
            if "navigationEndpoint" in data and "browseEndpoint" in data["navigationEndpoint"]:
                album["browseId"] = data["navigationEndpoint"]["browseEndpoint"]["browseId"]
            
            # Get playlistId from menu if available
            album["playlistId"] = nav(data, MENU_PLAYLIST_ID, none_if_absent=True)
            
            # Get title from title.runs[0].text
            album["title"] = nav(data, TITLE_TEXT)
            
            # Get thumbnails from thumbnailRenderer
            album["thumbnails"] = nav(data, THUMBNAIL_RENDERER)
            
            # Parse subtitle for type and year information
            if "subtitle" in data and "runs" in data["subtitle"]:
                subtitle_runs = data["subtitle"]["runs"]
                if subtitle_runs:
                    # First run is usually the type (Album, Single, etc.)
                    album["type"] = subtitle_runs[0]["text"]
                    
                    # Look for year in the subtitle runs
                    for run in subtitle_runs:
                        text = run["text"]
                        if text.strip().isdigit() and len(text.strip()) == 4:
                            album["year"] = text.strip()
                            break
                    
                    # Try to get more metadata from runs (similar to parse_song_runs)
                    if len(subtitle_runs) > 2:
                        # Skip type and separator, parse remaining runs
                        remaining_runs = [run for run in subtitle_runs[2:] if run["text"].strip() not in ["•", " • "]]
                        if remaining_runs:
                            for run in remaining_runs:
                                text = run["text"].strip()
                                if text.isdigit() and len(text) == 4:
                                    album["year"] = text
                                elif "song" in text.lower():
                                    album["songCount"] = text
            
            # Set album type if not already set
            if "type" not in album:
                album["type"] = "Album"  # default
            
            albums.append(album)
        
        return albums

    def _parse_ios_albums_new_format(self, contents: JsonList) -> JsonList:
        """
        Parse albums from new iOS elementRenderer format (musicListItemCarouselModel)
        """
        albums = []
        
        for item in contents:
            try:
                album = {}
                
                # Extract title
                if "title" in item:
                    album["title"] = item["title"]
                
                # Extract album browse ID from onTap command
                if ("onTap" in item and 
                    "innertubeCommand" in item["onTap"] and 
                    "browseEndpoint" in item["onTap"]["innertubeCommand"] and
                    "browseId" in item["onTap"]["innertubeCommand"]["browseEndpoint"]):
                    album["browseId"] = item["onTap"]["innertubeCommand"]["browseEndpoint"]["browseId"]
                    
                    # Extract playlist ID if available
                    browse_config = item["onTap"]["innertubeCommand"]["browseEndpoint"].get("browseEndpointContextSupportedConfigs")
                    if (browse_config and 
                        "browseEndpointContextMusicConfig" in browse_config and
                        "playlistIdForFallback" in browse_config["browseEndpointContextMusicConfig"]):
                        album["audioPlaylistId"] = browse_config["browseEndpointContextMusicConfig"]["playlistIdForFallback"]
                
                # Extract subtitle (artist info)
                if "subtitle" in item:
                    album["subtitle"] = item["subtitle"]
                
                # Extract thumbnail
                if ("thumbnail" in item and 
                    "image" in item["thumbnail"] and 
                    "sources" in item["thumbnail"]["image"]):
                    album["thumbnails"] = item["thumbnail"]["image"]["sources"]
                
                # Set default type
                album["type"] = "Album"
                album["isExplicit"] = False
                
                albums.append(album)
                
            except (KeyError, TypeError, IndexError):
                # Skip items that can't be parsed
                continue
        
        return albums

    ArtistOrderType = Literal["Recency", "Popularity", "Alphabetical order"]

    def get_artist_albums(
        self, channelId: str, params: str, limit: int | None = 100, order: ArtistOrderType | None = None
    ) -> JsonList:
        """
        Get the full list of an artist's albums, singles or shows

        :param channelId: browseId of the artist as returned by :py:func:`get_artist`
        :param params: params obtained by :py:func:`get_artist`
        :param limit: Number of albums to return. ``None`` retrieves them all. Default: 100
        :param order: Order of albums to return. Allowed values: ``Recency``, ``Popularity``, `Alphabetical order`. Default: Default order.
        :return: List of albums in the format of :py:func:`get_library_albums`,
          except artists key is missing.

        """
        body = {"browseId": channelId, "params": params}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        request_func: RequestFuncType = lambda additionalParams: self._send_request(
            endpoint, body, additionalParams
        )
        parse_func: ParseFuncType = lambda contents: parse_albums(contents)

        if order:
            # pick the correct continuation from response depending on the order chosen
            sort_options = nav(
                response,
                SINGLE_COLUMN_TAB
                + SECTION
                + HEADER_SIDE
                + [
                    "endItems",
                    0,
                    "musicSortFilterButtonRenderer",
                    "menu",
                    "musicMultiSelectMenuRenderer",
                    "options",
                ],
            )
            continuation = next(
                (
                    nav(
                        option,
                        [
                            *MULTI_SELECT,
                            "selectedCommand",
                            "commandExecutorCommand",
                            "commands",
                            -1,
                            "browseSectionListReloadEndpoint",
                        ],
                    )
                    for option in sort_options
                    if nav(option, MULTI_SELECT + TITLE_TEXT).lower() == order.lower()
                ),
                None,
            )
            # if a valid order was provided, request continuation and replace original response
            if continuation:
                additionalParams = get_reloadable_continuation_params(
                    {"continuations": [continuation["continuation"]]}
                )
                response = request_func(additionalParams)
                results = nav(response, SECTION_LIST_CONTINUATION + CONTENT)
            else:
                raise ValueError(f"Invalid order parameter {order}")

        else:
            # just use the results from the first request
            results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM)

        # Handle iOS format with elementRenderer structure
        try:
            contents = nav(results, GRID_ITEMS, True) or nav(results, CAROUSEL_CONTENTS)
        except (KeyError, TypeError):
            contents = None
        
        # If standard navigation fails, try iOS elementRenderer format
        if contents is None:
            try:
                # Check for iOS elementRenderer format
                if "itemSectionRenderer" in results and "contents" in results["itemSectionRenderer"]:
                    section_contents = results["itemSectionRenderer"]["contents"]
                    if (len(section_contents) > 0 and 
                        "elementRenderer" in section_contents[0] and
                        "newElement" in section_contents[0]["elementRenderer"]):
                        
                        element = section_contents[0]["elementRenderer"]["newElement"]
                        if ("type" in element and 
                            "componentType" in element["type"] and
                            "model" in element["type"]["componentType"] and
                            "musicListItemCarouselModel" in element["type"]["componentType"]["model"]):
                            
                            carousel_model = element["type"]["componentType"]["model"]["musicListItemCarouselModel"]
                            if "items" in carousel_model:
                                contents = carousel_model["items"]
            except (KeyError, IndexError, TypeError):
                # If iOS parsing fails, contents remains None
                pass
        
        # Check if we have iOS format (different structure for albums)
        ios_format_detected = False
        if contents and len(contents) > 0:
            # Check for new iOS elementRenderer format (from musicListItemCarouselModel)
            first_item = contents[0]
            if ("title" in first_item and 
                "subtitle" in first_item and 
                "onTap" in first_item and
                "innertubeCommand" in first_item["onTap"]):
                # This is the new iOS format from elementRenderer
                ios_format_detected = True
                albums = self._parse_ios_albums_new_format(contents)
            elif "musicTwoRowItemRenderer" in first_item:
                # Check if this is standard iOS format
                renderer = first_item["musicTwoRowItemRenderer"]
                is_ios_format = (
                    "navigationEndpoint" in renderer and 
                    "title" in renderer and 
                    "runs" in renderer["title"] and
                    "navigationEndpoint" not in renderer["title"]["runs"][0]
                )
                
                if is_ios_format:
                    ios_format_detected = True
                    albums = self._parse_ios_albums(contents)
                else:
                    albums = parse_albums(contents)
            else:
                albums = parse_albums(contents)
                
            # Apply limit for iOS format
            if ios_format_detected and limit is not None and len(albums) > limit:
                albums = albums[:limit]
        else:
            albums = parse_albums(contents) if contents else []

        # Handle continuations only for non-iOS format
        if not ios_format_detected:
            results = nav(results, GRID, True)
            if "continuations" in results:
                remaining_limit = None if limit is None else (limit - len(albums))
                albums.extend(
                    get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_func)
                )

        return albums

    def get_user(self, channelId: str) -> JsonDict:
        """
        Retrieve a user's page. A user may own videos or playlists.

        Use :py:func:`get_user_playlists` to retrieve all playlists::

            result = get_user(channelId)
            get_user_playlists(channelId, result["playlists"]["params"])

        Similarly, use :py:func:`get_user_videos` to retrieve all videos::

            get_user_videos(channelId, result["videos"]["params"])

        :param channelId: channelId of the user
        :return: Dictionary with information about a user.

        Example::

            {
              "name": "4Tune - No Copyright Music",
              "videos": {
                "browseId": "UC44hbeRoCZVVMVg5z0FfIww",
                "results": [
                  {
                    "title": "Epic Music Soundtracks 2019",
                    "videoId": "bJonJjgS2mM",
                    "playlistId": "RDAMVMbJonJjgS2mM",
                    "thumbnails": [
                      {
                        "url": "https://i.ytimg.com/vi/bJon...",
                        "width": 800,
                        "height": 450
                      }
                    ],
                    "views": "19K"
                  }
                ]
              },
              "playlists": {
                "browseId": "UC44hbeRoCZVVMVg5z0FfIww",
                "results": [
                  {
                    "title": "♚ Machinimasound | Playlist",
                    "playlistId": "PLRm766YvPiO9ZqkBuEzSTt6Bk4eWIr3gB",
                    "thumbnails": [
                      {
                        "url": "https://i.ytimg.com/vi/...",
                        "width": 400,
                        "height": 225
                      }
                    ]
                  }
                ],
                "params": "6gO3AUNvWU..."
              }
            }
        """
        endpoint = "browse"
        body = {"browseId": channelId}
        response = self._send_request(endpoint, body)
        user = {"name": nav(response, [*HEADER_MUSIC_VISUAL, *TITLE_TEXT])}
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        # Check if this is iOS format with elementRenderer structures
        if (results and len(results) > 0 
            and "itemSectionRenderer" in results[0] 
            and "contents" in results[0]["itemSectionRenderer"]
            and len(results[0]["itemSectionRenderer"]["contents"]) > 0
            and "elementRenderer" in results[0]["itemSectionRenderer"]["contents"][0]):
            user.update(self._parse_ios_user_contents(results))
        else:
            user.update(self.parser.parse_channel_contents(results))
        return user

    def _parse_ios_user_contents(self, results: JsonList) -> JsonDict:
        """Parse user contents in iOS format with elementRenderer structures"""
        from ytmusicapi.parsers.browsing import parse_album, parse_playlist, parse_video, parse_single, parse_related_artist
        from ytmusicapi.parsers.podcasts import parse_episode, parse_podcast
        from ytmusicapi.navigation import MTRIR, MMRIR
        
        categories = [
            ("albums", "albums", parse_album, MTRIR),
            ("singles", "singles & eps", parse_single, MTRIR),
            ("shows", "shows", parse_album, MTRIR),
            ("videos", "videos", parse_video, MTRIR),
            ("playlists", "playlists", parse_playlist, MTRIR),
            ("related", "fans might also like", parse_related_artist, MTRIR),
            ("episodes", "episodes", parse_episode, MMRIR),
            ("podcasts", "podcasts", parse_podcast, MTRIR),
        ]
        
        user_contents = {}
        
        for section in results:
            if "itemSectionRenderer" not in section:
                continue
                
            item_section = section["itemSectionRenderer"]
            if "contents" not in item_section:
                continue
                
            for content_item in item_section["contents"]:
                if "elementRenderer" not in content_item:
                    continue
                    
                element = content_item["elementRenderer"]
                
                # Navigate to the nested content structure
                if ("newElement" in element 
                    and "type" in element["newElement"] 
                    and "componentType" in element["newElement"]["type"]
                    and "model" in element["newElement"]["type"]["componentType"]):
                    
                    model = element["newElement"]["type"]["componentType"]["model"]
                    
                    # Handle musicListItemCarouselModel (e.g., Top songs)
                    if "musicListItemCarouselModel" in model:
                        carousel = model["musicListItemCarouselModel"]
                        
                        # Get the title/category
                        section_title = None
                        if "header" in carousel and "title" in carousel["header"]:
                            section_title = carousel["header"]["title"].lower()
                        
                        # Special handling for "Top songs" -> "videos"
                        if section_title == "top songs":
                            section_title = "videos"
                        
                        if section_title:
                            items = self._parse_ios_list_items(carousel.get("items", []))
                            
                            # Find matching category
                            for category, category_local, category_parser, category_key in categories:
                                if category == section_title or category_local.lower() == section_title:
                                    if items:
                                        user_contents[category] = {
                                            "browseId": None,
                                            "results": items
                                        }
                                        
                                        # Extract browseId if available
                                        if ("header" in carousel 
                                            and "onTap" in carousel["header"] 
                                            and "innertubeCommand" in carousel["header"]["onTap"]
                                            and "browseEndpoint" in carousel["header"]["onTap"]["innertubeCommand"]):
                                            
                                            browse_endpoint = carousel["header"]["onTap"]["innertubeCommand"]["browseEndpoint"]
                                            if "browseId" in browse_endpoint:
                                                user_contents[category]["browseId"] = browse_endpoint["browseId"]
                                            if "params" in browse_endpoint:
                                                user_contents[category]["params"] = browse_endpoint["params"]
                                    break
                    
                    # Handle musicGridItemCarouselModel (e.g., Albums, Singles, Playlists)
                    elif "musicGridItemCarouselModel" in model:
                        carousel = model["musicGridItemCarouselModel"]
                        
                        if "shelf" in carousel:
                            shelf = carousel["shelf"]
                            
                            # Get the title/category
                            section_title = None
                            if "header" in shelf and "title" in shelf["header"]:
                                section_title = shelf["header"]["title"].lower()
                            
                            if section_title:
                                items = self._parse_ios_grid_items(shelf.get("items", []))
                                
                                # Find matching category
                                for category, category_local, category_parser, category_key in categories:
                                    if category == section_title or category_local.lower() == section_title:
                                        if items:
                                            user_contents[category] = {
                                                "browseId": None,
                                                "results": items
                                            }
                                            
                                            # Extract browseId if available
                                            if ("header" in shelf 
                                                and "onTap" in shelf["header"] 
                                                and "innertubeCommand" in shelf["header"]["onTap"]
                                                and "browseEndpoint" in shelf["header"]["onTap"]["innertubeCommand"]):
                                                
                                                browse_endpoint = shelf["header"]["onTap"]["innertubeCommand"]["browseEndpoint"]
                                                if "browseId" in browse_endpoint:
                                                    user_contents[category]["browseId"] = browse_endpoint["browseId"]
                                                if "params" in browse_endpoint:
                                                    user_contents[category]["params"] = browse_endpoint["params"]
                                        break
        
        return user_contents
    
    def _parse_ios_list_items(self, items: JsonList) -> JsonList:
        """Parse items from musicListItemCarouselModel"""
        parsed_items = []
        
        for item in items:
            try:
                parsed_item = {}
                
                # Extract title
                if "title" in item:
                    if isinstance(item["title"], dict) and "text" in item["title"]:
                        parsed_item["title"] = item["title"]["text"]
                    elif isinstance(item["title"], str):
                        parsed_item["title"] = item["title"]
                
                # Extract subtitle (artist info)
                if "subtitle" in item:
                    if isinstance(item["subtitle"], dict) and "runs" in item["subtitle"]:
                        # Join all runs for subtitle
                        subtitle_parts = [run["text"] for run in item["subtitle"]["runs"]]
                        parsed_item["subtitle"] = "".join(subtitle_parts)
                    elif isinstance(item["subtitle"], str):
                        parsed_item["subtitle"] = item["subtitle"]
                
                # Extract navigation endpoints for IDs
                if "onTap" in item and "innertubeCommand" in item["onTap"]:
                    command = item["onTap"]["innertubeCommand"]
                    
                    if "browseEndpoint" in command:
                        browse_endpoint = command["browseEndpoint"]
                        if "browseId" in browse_endpoint:
                            parsed_item["browseId"] = browse_endpoint["browseId"]
                    
                    elif "watchEndpoint" in command:
                        watch_endpoint = command["watchEndpoint"]
                        if "videoId" in watch_endpoint:
                            parsed_item["videoId"] = watch_endpoint["videoId"]
                        if "playlistId" in watch_endpoint:
                            parsed_item["playlistId"] = watch_endpoint["playlistId"]
                
                # Extract thumbnails - handle both complex and simple thumbnail structures
                if "thumbnail" in item:
                    if "musicThumbnailRenderer" in item["thumbnail"]:
                        # Complex structure
                        thumbnail_renderer = item["thumbnail"]["musicThumbnailRenderer"]
                        if "thumbnail" in thumbnail_renderer and "thumbnails" in thumbnail_renderer["thumbnail"]:
                            parsed_item["thumbnails"] = thumbnail_renderer["thumbnail"]["thumbnails"]
                    elif "image" in item["thumbnail"] and "sources" in item["thumbnail"]["image"]:
                        # Simple structure - convert to expected format
                        sources = item["thumbnail"]["image"]["sources"]
                        thumbnails = []
                        for source in sources:
                            if "url" in source:
                                thumbnail = {"url": source["url"]}
                                if "width" in source:
                                    thumbnail["width"] = source["width"]
                                if "height" in source:
                                    thumbnail["height"] = source["height"]
                                thumbnails.append(thumbnail)
                        if thumbnails:
                            parsed_item["thumbnails"] = thumbnails
                
                if parsed_item:  # Only add if we extracted some data
                    parsed_items.append(parsed_item)
                    
            except Exception:
                continue  # Skip items we can't parse
        
        return parsed_items
    
    def _parse_ios_grid_items(self, items: JsonList) -> JsonList:
        """Parse items from musicGridItemCarouselModel"""
        parsed_items = []
        
        for item in items:
            try:
                parsed_item = {}
                
                # Extract title - it's directly in the item
                if "title" in item:
                    if isinstance(item["title"], str):
                        parsed_item["title"] = item["title"]
                    elif isinstance(item["title"], dict) and "text" in item["title"]:
                        parsed_item["title"] = item["title"]["text"]
                
                # Extract subtitle - it's directly in the item
                if "subtitle" in item:
                    if isinstance(item["subtitle"], str):
                        parsed_item["subtitle"] = item["subtitle"]
                    elif isinstance(item["subtitle"], dict) and "runs" in item["subtitle"]:
                        # Join all runs for subtitle
                        subtitle_parts = [run["text"] for run in item["subtitle"]["runs"]]
                        parsed_item["subtitle"] = "".join(subtitle_parts)
                
                # Extract navigation endpoints for IDs
                if "onTap" in item and "innertubeCommand" in item["onTap"]:
                    command = item["onTap"]["innertubeCommand"]
                    
                    if "browseEndpoint" in command:
                        browse_endpoint = command["browseEndpoint"]
                        if "browseId" in browse_endpoint:
                            parsed_item["browseId"] = browse_endpoint["browseId"]
                    
                    elif "watchEndpoint" in command:
                        watch_endpoint = command["watchEndpoint"]
                        if "videoId" in watch_endpoint:
                            parsed_item["videoId"] = watch_endpoint["videoId"]
                        if "playlistId" in watch_endpoint:
                            parsed_item["playlistId"] = watch_endpoint["playlistId"]
                
                # Extract thumbnails - handle both complex and simple thumbnail structures
                if "thumbnail" in item:
                    if "musicThumbnailRenderer" in item["thumbnail"]:
                        # Complex structure
                        thumbnail_renderer = item["thumbnail"]["musicThumbnailRenderer"]
                        if "thumbnail" in thumbnail_renderer and "thumbnails" in thumbnail_renderer["thumbnail"]:
                            parsed_item["thumbnails"] = thumbnail_renderer["thumbnail"]["thumbnails"]
                    elif "image" in item["thumbnail"] and "sources" in item["thumbnail"]["image"]:
                        # Simple structure - convert to expected format
                        sources = item["thumbnail"]["image"]["sources"]
                        thumbnails = []
                        for source in sources:
                            if "url" in source:
                                thumbnail = {"url": source["url"]}
                                if "width" in source:
                                    thumbnail["width"] = source["width"]
                                if "height" in source:
                                    thumbnail["height"] = source["height"]
                                thumbnails.append(thumbnail)
                        if thumbnails:
                            parsed_item["thumbnails"] = thumbnails
                
                if parsed_item:  # Only add if we extracted some data
                    parsed_items.append(parsed_item)
                    
            except Exception:
                continue  # Skip items we can't parse
        
        return parsed_items

    def get_user_playlists(self, channelId: str, params: str) -> JsonList:
        """
        Retrieve a list of playlists for a given user.
        Call this function again with the returned ``params`` to get the full list.

        :param channelId: channelId of the user.
        :param params: params obtained by :py:func:`get_user`
        :return: List of user playlists in the format of :py:func:`get_library_playlists`

        """
        endpoint = "browse"
        body = {"browseId": channelId, "params": params}
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + GRID_ITEMS, True)
        if not results:
            return []

        # Check if this is iOS format with musicTwoRowItemRenderer
        if results and len(results) > 0 and 'musicTwoRowItemRenderer' in results[0]:
            user_playlists = self._parse_ios_user_playlists(results)
        else:
            user_playlists = parse_content_list(results, parse_playlist)

        return user_playlists

    def _parse_ios_user_playlists(self, results: JsonList) -> JsonList:
        """Parse user playlists in iOS format with musicTwoRowItemRenderer"""
        playlists = []
        
        for item in results:
            try:
                if 'musicTwoRowItemRenderer' not in item:
                    continue
                    
                renderer = item['musicTwoRowItemRenderer']
                playlist = {}
                
                # Extract title
                if 'title' in renderer and 'runs' in renderer['title']:
                    title_runs = renderer['title']['runs']
                    if title_runs and len(title_runs) > 0:
                        playlist['title'] = title_runs[0]['text']
                
                # Extract playlistId from navigationEndpoint (iOS format has it at top level)
                if 'navigationEndpoint' in renderer and 'browseEndpoint' in renderer['navigationEndpoint']:
                    browse_endpoint = renderer['navigationEndpoint']['browseEndpoint']
                    if 'browseId' in browse_endpoint:
                        browse_id = browse_endpoint['browseId']
                        # Remove VL prefix to get playlist ID
                        if browse_id.startswith('VL'):
                            playlist['playlistId'] = browse_id[2:]
                        else:
                            playlist['playlistId'] = browse_id
                
                # Extract thumbnails
                if 'thumbnailRenderer' in renderer and 'musicThumbnailRenderer' in renderer['thumbnailRenderer']:
                    thumbnail_renderer = renderer['thumbnailRenderer']['musicThumbnailRenderer']
                    if 'thumbnail' in thumbnail_renderer and 'thumbnails' in thumbnail_renderer['thumbnail']:
                        playlist['thumbnails'] = thumbnail_renderer['thumbnail']['thumbnails']
                
                # Extract description and metadata from subtitle
                if 'subtitle' in renderer and 'runs' in renderer['subtitle']:
                    subtitle_runs = renderer['subtitle']['runs']
                    description_parts = []
                    
                    for run in subtitle_runs:
                        description_parts.append(run['text'])
                    
                    full_description = ''.join(description_parts)
                    playlist['description'] = full_description
                    
                    # Try to extract count and author from subtitle
                    # Format is usually: "Playlist • Author • X views" or "Playlist • Author • X songs"
                    if len(subtitle_runs) >= 3:
                        # Look for view count or song count
                        for run in subtitle_runs:
                            text = run['text']
                            if ' views' in text or ' songs' in text or ' song' in text:
                                # Extract number
                                import re
                                match = re.search(r'(\d+(?:\.\d+)?[KMB]?)\s+(?:views?|songs?)', text)
                                if match:
                                    playlist['count'] = match.group(1)
                                break
                        
                        # Extract author (usually between "Playlist •" and "• X views/songs")
                        if len(subtitle_runs) >= 5:  # Playlist • Author • X views
                            author_run = subtitle_runs[2]
                            if author_run['text'] != ' • ':
                                playlist['author'] = [{'name': author_run['text'], 'id': None}]
                
                if playlist:  # Only add if we extracted some data
                    playlists.append(playlist)
                    
            except Exception:
                continue  # Skip items we can't parse
        
        return playlists

    def get_user_videos(self, channelId: str, params: str) -> JsonList:
        """
        Retrieve a list of videos for a given user.
        Call this function again with the returned ``params`` to get the full list.

        :param channelId: channelId of the user.
        :param params: params obtained by :py:func:`get_user`
        :return: List of user videos

        """
        endpoint = "browse"
        body = {"browseId": channelId, "params": params}
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + GRID_ITEMS, True)
        if not results:
            # Try iOS format with musicPlaylistShelfRenderer
            section_content = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM, True)
            if section_content and 'musicPlaylistShelfRenderer' in section_content:
                shelf_contents = section_content['musicPlaylistShelfRenderer'].get('contents', [])
                if shelf_contents:
                    return self._parse_ios_user_videos(shelf_contents)
            return []

        user_videos = parse_content_list(results, parse_video)

        return user_videos

    def _parse_ios_user_videos(self, contents: JsonList) -> JsonList:
        """
        Parse user videos from iOS format musicPlaylistShelfRenderer contents.
        
        :param contents: List of video items from musicPlaylistShelfRenderer
        :return: List of parsed video dictionaries
        """
        videos = []
        for item in contents:
            if 'musicTwoColumnItemRenderer' in item:
                renderer = item['musicTwoColumnItemRenderer']
                
                try:
                    video = {}
                    
                    # Extract title
                    if 'title' in renderer and 'runs' in renderer['title']:
                        video['title'] = renderer['title']['runs'][0]['text']
                    
                    # Extract videoId from navigationEndpoint
                    if 'navigationEndpoint' in renderer and 'watchEndpoint' in renderer['navigationEndpoint']:
                        watch_endpoint = renderer['navigationEndpoint']['watchEndpoint']
                        video['videoId'] = watch_endpoint.get('videoId', '')
                    
                    # Extract thumbnails
                    if 'thumbnail' in renderer and 'musicThumbnailRenderer' in renderer['thumbnail']:
                        thumbnail_renderer = renderer['thumbnail']['musicThumbnailRenderer']
                        if 'thumbnail' in thumbnail_renderer and 'thumbnails' in thumbnail_renderer['thumbnail']:
                            video['thumbnails'] = thumbnail_renderer['thumbnail']['thumbnails']
                    
                    # Extract metadata from subtitle
                    if 'subtitle' in renderer and 'runs' in renderer['subtitle']:
                        subtitle_runs = renderer['subtitle']['runs']
                        if len(subtitle_runs) >= 3:
                            # Format is typically: "Artist • Duration" or similar
                            video['artists'] = [{'name': subtitle_runs[0]['text']}]
                            # Duration is usually the last run
                            for run in subtitle_runs:
                                if ':' in run['text']:  # Duration format like "3:45"
                                    video['duration'] = run['text']
                                    break
                    
                    # Only add if we have the essential fields
                    if 'title' in video and 'videoId' in video:
                        videos.append(video)
                        
                except Exception as e:
                    # Skip malformed items
                    continue
        
        return videos

    def get_album_browse_id(self, audioPlaylistId: str) -> str | None:
        """
        Get an album's browseId based on its audioPlaylistId

        :param audioPlaylistId: id of the audio playlist  (starting with `OLAK5uy_`)
        :return: browseId (starting with ``MPREb_``)
        """
        params = {"list": audioPlaylistId}
        response = self._send_get_request(YTM_DOMAIN + "/playlist", params)

        with warnings.catch_warnings():
            # merge this with statement with catch_warnings on Python>=3.11
            warnings.simplefilter(action="ignore", category=DeprecationWarning)
            decoded = response.text.encode("utf8").decode("unicode_escape")

        matches = re.search(r"\"MPRE.+?\"", decoded)
        browse_id = None
        if matches:
            browse_id = matches.group().strip('"')
        return browse_id

    def get_album(self, browseId: str) -> JsonDict:
        """
        Get information and tracks of an album

        :param browseId: browseId of the album, for example
            returned by :py:func:`search`
        :return: Dictionary with album and track metadata.

        The result is in the following format::

            {
              "title": "Revival",
              "type": "Album",
              "thumbnails": [],
              "description": "Revival is the...",
              "artists": [
                {
                  "name": "Eminem",
                  "id": "UCedvOgsKFzcK3hA5taf3KoQ"
                }
              ],
              "year": "2017",
              "trackCount": 19,
              "duration": "1 hour, 17 minutes",
              "audioPlaylistId": "OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY",
              "tracks": [
                {
                  "videoId": "iKLU7z_xdYQ",
                  "title": "Walk On Water (feat. Beyoncé)",
                  "artists": [
                    {
                      "name": "Eminem",
                      "id": "UCedvOgsKFzcK3hA5taf3KoQ"
                    }
                  ],
                  "album": "Revival",
                  "likeStatus": "INDIFFERENT",
                  "thumbnails": null,
                  "isAvailable": true,
                  "isExplicit": true,
                  "duration": "5:03",
                  "duration_seconds": 303,
                  "trackNumber": 0,
                  "feedbackTokens": {
                    "add": "AB9zfpK...",
                    "remove": "AB9zfpK..."
                  }
                }
              ],
              "other_versions": [
                {
                  "title": "Revival",
                  "year": "Eminem",
                  "browseId": "MPREb_fefKFOTEZSp",
                  "thumbnails": [...],
                  "isExplicit": false
                },
              ],
              "duration_seconds": 4657
            }
        """
        if not browseId or not browseId.startswith("MPRE"):
            raise YTMusicUserError("Invalid album browseId provided, must start with MPRE.")

        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        
        # Check for iOS format (singleColumnBrowseResultsRenderer)
        if 'singleColumnBrowseResultsRenderer' in response['contents']:
            return self._parse_ios_album(response)
        
        # Traditional format (twoColumnBrowseResultsRenderer)
        album: JsonDict = parse_album_header_2024(response)

        results = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF])
        album["tracks"] = parse_playlist_items(results["contents"], is_album=True)

        secondary_carousels = (
            nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION_LIST], True) or []
        )
        for section in secondary_carousels[1:]:
            carousel = nav(section, CAROUSEL)
            key = {
                "COLLECTION_STYLE_ITEM_SIZE_SMALL": "related_recommendations",
                "COLLECTION_STYLE_ITEM_SIZE_MEDIUM": "other_versions",
            }[carousel["itemSize"]]
            album[key] = parse_content_list(carousel["contents"], parse_album)

        album["duration_seconds"] = sum_total_duration(album)
        for i, track in enumerate(album["tracks"]):
            album["tracks"][i]["album"] = album["title"]
            album["tracks"][i]["artists"] = album["tracks"][i]["artists"] or album["artists"]

        return album

    def _parse_ios_album(self, response: JsonDict) -> JsonDict:
        """Parse album response from iOS format (singleColumnBrowseResultsRenderer)"""
        # Get header from musicElementHeaderRenderer
        header = nav(response, ["header", "musicElementHeaderRenderer"])
        
        # Initialize album dict
        album: JsonDict = {}
        
        # Extract data from nested elementRenderer structure
        data = nav(header, ["elementRenderer", "elementRenderer", "newElement", "type", "componentType", "model", "musicBlurredBackgroundHeaderModel", "data"], True) or {}
        
        # Parse basic album info
        album["title"] = data.get("title", "")
        album["type"] = "Album"
        
        # Get thumbnails from primaryImage
        album["thumbnails"] = nav(data, ["primaryImage", "sources"], True) or []
        
        # Parse artist and year from straplineData
        album["artists"] = []
        album["year"] = None
        album["trackCount"] = None
        album["tracks"] = []
        album["duration"] = None
        album["audioPlaylistId"] = None
        album["likeStatus"] = "INDIFFERENT"
        album["isExplicit"] = False
        
        # Artist from straplineData.textLine1
        artist_name = nav(data, ["straplineData", "textLine1", "content"], True)
        if artist_name:
            # Try to get artist ID from menu (if available)
            artist_id = None
            menu_renderer = nav(header, ["elementRenderer", "elementRenderer", "newElement", "type", "componentType", "model", "musicBlurredBackgroundHeaderModel", "data", "actionButtons", 3, "button", "onTap", "innertubeCommand", "menuEndpoint", "menu", "menuRenderer"], True)
            if menu_renderer:
                # Look for "Go to artist" menu item
                for item in menu_renderer.get("items", []):
                    if "menuNavigationItemRenderer" in item:
                        item_renderer = item["menuNavigationItemRenderer"]
                        text = nav(item_renderer, ["text", "runs", 0, "text"], True)
                        if text == "Go to artist":
                            artist_id = nav(item_renderer, ["navigationEndpoint", "browseEndpoint", "browseId"], True)
                            break
            
            album["artists"].append({
                "name": artist_name,
                "id": artist_id
            })
        
        # Year from straplineData.textLine2 (e.g., "Album • 2024")
        year_text = nav(data, ["straplineData", "textLine2", "content"], True) or ""
        import re
        year_match = re.search(r'(\d{4})', year_text)
        if year_match:
            album["year"] = year_match.group(1)
        
        # Get description
        album["description"] = data.get("description")
        
        # Get track count from menu if available
        menu_renderer = nav(header, ["elementRenderer", "elementRenderer", "newElement", "type", "componentType", "model", "musicBlurredBackgroundHeaderModel", "data", "actionButtons", 3, "button", "onTap", "innertubeCommand", "menuEndpoint", "menu", "menuRenderer"], True)
        if menu_renderer:
            secondary_text = nav(menu_renderer, ["title", "musicMenuTitleRenderer", "secondaryText", "runs"], True)
            if secondary_text:
                for run in secondary_text:
                    text = run.get("text", "")
                    if "song" in text.lower():
                        # Extract track count from text like "12 songs"
                        match = re.search(r'(\d+)', text)
                        if match:
                            album["trackCount"] = int(match.group(1))
                        break
        
        # Get sections from singleColumnBrowseResultsRenderer
        sections = []
        if "contents" in response and "singleColumnBrowseResultsRenderer" in response["contents"]:
            single_col = response["contents"]["singleColumnBrowseResultsRenderer"]
            if "tabs" in single_col and single_col["tabs"]:
                tab_content = single_col["tabs"][0].get("tabRenderer", {}).get("content", {})
                if "sectionListRenderer" in tab_content:
                    sections = tab_content["sectionListRenderer"].get("contents", [])
        
        # Parse each section
        for section in sections:
            if "musicPlaylistShelfRenderer" in section:
                # This is the tracks section (traditional format)
                shelf = section["musicPlaylistShelfRenderer"]
                
                # Get audioPlaylistId from playlistId
                if "playlistId" in shelf:
                    album["audioPlaylistId"] = shelf["playlistId"]
                
                # Parse tracks using existing function (need to import parse_playlist_items)
                if "contents" in shelf:
                    # For now, skip traditional parsing as we're focusing on iOS
                    pass
                
            elif "itemSectionRenderer" in section:
                # iOS format - individual track sections
                item_section = section["itemSectionRenderer"]
                contents = item_section.get("contents", [])
                
                if contents and "elementRenderer" in contents[0]:
                    element = contents[0]["elementRenderer"]
                    
                    try:
                        # Navigate to musicListItemWrapperModel
                        new_element = element.get("newElement", {})
                        type_info = new_element.get("type", {})
                        component_type = type_info.get("componentType", {})
                        model = component_type.get("model", {})
                        
                        if "musicListItemWrapperModel" in model:
                            wrapper_model = model["musicListItemWrapperModel"]
                            
                            if "musicListItemData" in wrapper_model:
                                item_data = wrapper_model["musicListItemData"]
                                
                                # Check if this is a track (has indexText)
                                if "indexText" in item_data and "title" in item_data:
                                    track = self._parse_ios_track(item_data, album)
                                    if track:
                                        album["tracks"].append(track)
                                        
                                        # Set audioPlaylistId from first track
                                        if not album["audioPlaylistId"] and track.get("playlistId"):
                                            album["audioPlaylistId"] = track["playlistId"]
                        
                    except (KeyError, TypeError):
                        # Not a track section, continue
                        pass
                
            # Skip carousel parsing for now
        
        # Calculate duration
        album["duration_seconds"] = sum_total_duration(album)
        
        # Add album metadata to tracks
        for i, track in enumerate(album["tracks"]):
            album["tracks"][i]["album"] = album["title"]
            album["tracks"][i]["artists"] = album["tracks"][i]["artists"] or album["artists"]
        
        return album
    
    def _parse_ios_track(self, item_data: JsonDict, album: JsonDict) -> JsonDict:
        """Parse individual track from iOS musicListItemData"""
        track = {
            'videoId': None,
            'title': item_data.get('title', ''),
            'artists': [],
            'album': album.get('title', ''),
            'likeStatus': 'INDIFFERENT',
            'thumbnails': album.get('thumbnails', []),
            'isAvailable': True,
            'isExplicit': False,
            'videoType': 'MUSIC_VIDEO_TYPE_ATV',
            'duration': None,
            'duration_seconds': None,
            'feedbackTokens': None,
            'playlistId': None
        }
        
        # Extract videoId and playlistId from onTap
        if 'onTap' in item_data and 'innertubeCommand' in item_data['onTap']:
            command = item_data['onTap']['innertubeCommand']
            if 'watchEndpoint' in command:
                watch = command['watchEndpoint']
                track['videoId'] = watch.get('videoId')
                track['playlistId'] = watch.get('playlistId')
        
        # Parse artist and duration from subtitle (format: "Artist • Duration • Plays")
        subtitle = item_data.get('subtitle', '')
        if subtitle:
            parts = subtitle.split('•')
            if len(parts) >= 2:
                # Artist
                artist_name = parts[0].strip()
                if artist_name:
                    track['artists'] = [{'name': artist_name, 'id': None}]
                
                # Duration
                duration_part = parts[1].strip()
                track['duration'] = duration_part
                
                # Convert to seconds
                if ':' in duration_part:
                    time_parts = duration_part.split(':')
                    if len(time_parts) == 2:
                        try:
                            minutes = int(time_parts[0])
                            seconds = int(time_parts[1])
                            track['duration_seconds'] = minutes * 60 + seconds
                        except ValueError:
                            pass
        
        return track

    def get_song(self, videoId: str, signatureTimestamp: int | None = None) -> JsonDict:
        """
        Returns metadata and streaming information about a song or video.

        :param videoId: Video id
        :param signatureTimestamp: Provide the current YouTube signatureTimestamp.
            If not provided a default value will be used, which might result in invalid streaming URLs
        :return: Dictionary with song metadata.

        Example::

            {
                "playabilityStatus": {
                    "status": "OK",
                    "playableInEmbed": true,
                    "audioOnlyPlayability": {
                        "audioOnlyPlayabilityRenderer": {
                            "trackingParams": "CAEQx2kiEwiuv9X5i5H1AhWBvlUKHRoZAHk=",
                            "audioOnlyAvailability": "FEATURE_AVAILABILITY_ALLOWED"
                        }
                    },
                    "miniplayer": {
                        "miniplayerRenderer": {
                            "playbackMode": "PLAYBACK_MODE_ALLOW"
                        }
                    },
                    "contextParams": "Q0FBU0FnZ0M="
                },
                "streamingData": {
                    "expiresInSeconds": "21540",
                    "adaptiveFormats": [
                        {
                            "itag": 140,
                            "url": "https://rr1---sn-h0jelnez.c.youtube.com/videoplayback?expire=1641080272...",
                            "mimeType": "audio/mp4; codecs=\"mp4a.40.2\"",
                            "bitrate": 131007,
                            "initRange": {
                                "start": "0",
                                "end": "667"
                            },
                            "indexRange": {
                                "start": "668",
                                "end": "999"
                            },
                            "lastModified": "1620321966927796",
                            "contentLength": "3967382",
                            "quality": "tiny",
                            "projectionType": "RECTANGULAR",
                            "averageBitrate": 129547,
                            "highReplication": true,
                            "audioQuality": "AUDIO_QUALITY_MEDIUM",
                            "approxDurationMs": "245000",
                            "audioSampleRate": "44100",
                            "audioChannels": 2,
                            "loudnessDb": -1.3000002
                        }
                    ]
                },
                "playbackTracking": {
                    "videostatsPlaybackUrl": {
                      "baseUrl": "https://s.youtube.com/api/stats/playback?cl=491307275&docid=AjXQiKP5kMs&ei=Nl2HY-6MH5WE8gPjnYnoDg&fexp=1714242%2C9405963%2C23804281%2C23858057%2C23880830%2C23880833%2C23882685%2C23918597%2C23934970%2C23946420%2C23966208%2C23983296%2C23998056%2C24001373%2C24002022%2C24002025%2C24004644%2C24007246%2C24034168%2C24036947%2C24077241%2C24080738%2C24120820%2C24135310%2C24135692%2C24140247%2C24161116%2C24162919%2C24164186%2C24169501%2C24175560%2C24181174%2C24187043%2C24187377%2C24187854%2C24191629%2C24197450%2C24199724%2C24200839%2C24209349%2C24211178%2C24217535%2C24219713%2C24224266%2C24241378%2C24248091%2C24248956%2C24255543%2C24255545%2C24262346%2C24263796%2C24265426%2C24267564%2C24268142%2C24279196%2C24280220%2C24283426%2C24283493%2C24287327%2C24288045%2C24290971%2C24292955%2C24293803%2C24299747%2C24390674%2C24391018%2C24391537%2C24391709%2C24392268%2C24392363%2C24392401%2C24401557%2C24402891%2C24403794%2C24406605%2C24407200%2C24407665%2C24407914%2C24408220%2C24411766%2C24413105%2C24413820%2C24414162%2C24415866%2C24416354%2C24420756%2C24421162%2C24425861%2C24428962%2C24590921%2C39322504%2C39322574%2C39322694%2C39322707&ns=yt&plid=AAXusD4TIOMjS5N4&el=detailpage&len=246&of=Jx1iRksbq-rB9N1KSijZLQ&osid=MWU2NzBjYTI%3AAOeUNAagU8UyWDUJIki5raGHy29-60-yTA&uga=29&vm=CAEQABgEOjJBUEV3RWxUNmYzMXNMMC1MYVpCVnRZTmZWMWw1OWVZX2ZOcUtCSkphQ245VFZwOXdTQWJbQVBta0tETEpWNXI1SlNIWEJERXdHeFhXZVllNXBUemt5UHR4WWZEVzFDblFUSmdla3BKX2R0dXk3bzFORWNBZmU5YmpYZnlzb3doUE5UU0FoVGRWa0xIaXJqSWgB",
                      "headers": [
                        {
                          "headerType": "USER_AUTH"
                        },
                        {
                          "headerType": "VISITOR_ID"
                        },
                        {
                          "headerType": "PLUS_PAGE_ID"
                        }
                      ]
                    },
                    "videostatsDelayplayUrl": {(as above)},
                    "videostatsWatchtimeUrl": {(as above)},
                    "ptrackingUrl": {(as above)},
                    "qoeUrl": {(as above)},
                    "atrUrl": {(as above)},
                    "videostatsScheduledFlushWalltimeSeconds": [
                      10,
                      20,
                      30
                    ],
                    "videostatsDefaultFlushIntervalSeconds": 40
                },
                "videoDetails": {
                    "videoId": "AjXQiKP5kMs",
                    "title": "Sparks",
                    "lengthSeconds": "245",
                    "channelId": "UCvCk2zFqkCYzpnSgWfx0qOg",
                    "isOwnerViewing": false,
                    "isCrawlable": false,
                    "thumbnail": {
                        "thumbnails": []
                    },
                    "allowRatings": true,
                    "viewCount": "12",
                    "author": "Thomas Bergersen",
                    "isPrivate": true,
                    "isUnpluggedCorpus": false,
                    "musicVideoType": "MUSIC_VIDEO_TYPE_PRIVATELY_OWNED_TRACK",
                    "isLiveContent": false
                },
                "microformat": {
                    "microformatDataRenderer": {
                        "urlCanonical": "https://music.youtube.com/watch?v=AjXQiKP5kMs",
                        "title": "Sparks - YouTube Music",
                        "description": "Uploaded to YouTube via YouTube Music Sparks",
                        "thumbnail": {
                            "thumbnails": [
                                {
                                    "url": "https://i.ytimg.com/vi/AjXQiKP5kMs/hqdefault.jpg",
                                    "width": 480,
                                    "height": 360
                                }
                            ]
                        },
                        "siteName": "YouTube Music",
                        "appName": "YouTube Music",
                        "androidPackage": "com.google.android.apps.youtube.music",
                        "iosAppStoreId": "1017492454",
                        "iosAppArguments": "https://music.youtube.com/watch?v=AjXQiKP5kMs",
                        "ogType": "video.other",
                        "urlApplinksIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks",
                        "urlApplinksAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks",
                        "urlTwitterIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link",
                        "urlTwitterAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link",
                        "twitterCardType": "player",
                        "twitterSiteHandle": "@YouTubeMusic",
                        "schemaDotOrgType": "http://schema.org/VideoObject",
                        "noindex": true,
                        "unlisted": true,
                        "paid": false,
                        "familySafe": true,
                        "pageOwnerDetails": {
                            "name": "Music Library Uploads",
                            "externalChannelId": "UCvCk2zFqkCYzpnSgWfx0qOg",
                            "youtubeProfileUrl": "http://www.youtube.com/channel/UCvCk2zFqkCYzpnSgWfx0qOg"
                        },
                        "videoDetails": {
                            "externalVideoId": "AjXQiKP5kMs",
                            "durationSeconds": "246",
                            "durationIso8601": "PT4M6S"
                        },
                        "linkAlternates": [
                            {
                                "hrefUrl": "android-app://com.google.android.youtube/http/youtube.com/watch?v=AjXQiKP5kMs"
                            },
                            {
                                "hrefUrl": "ios-app://544007664/http/youtube.com/watch?v=AjXQiKP5kMs"
                            },
                            {
                                "hrefUrl": "https://www.youtube.com/oembed?format=json&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs",
                                "title": "Sparks",
                                "alternateType": "application/json+oembed"
                            },
                            {
                                "hrefUrl": "https://www.youtube.com/oembed?format=xml&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs",
                                "title": "Sparks",
                                "alternateType": "text/xml+oembed"
                            }
                        ],
                        "viewCount": "12",
                        "publishDate": "1969-12-31",
                        "category": "Music",
                        "uploadDate": "1969-12-31"
                    }
                }
            }

        """
        # Try original player endpoint first for full functionality
        endpoint = "player"
        if not signatureTimestamp:
            signatureTimestamp = get_datestamp() - 1

        params = {
            "playbackContext": {"contentPlaybackContext": {"signatureTimestamp": signatureTimestamp}},
            "video_id": videoId,
        }
        
        try:
            response = self._send_request(endpoint, params)
            
            # Check if we got LOGIN_REQUIRED status
            playability_status = response.get("playabilityStatus", {})
            if playability_status.get("status") == "LOGIN_REQUIRED":
                # Fall back to 'next' endpoint for basic song metadata (iOS compatible)
                return self._get_song_fallback(videoId)
            
            # Original success path - return full response
            keys = ["videoDetails", "playabilityStatus", "streamingData", "microformat", "playbackTracking"]
            for k in list(response.keys()):
                if k not in keys:
                    del response[k]
            return response
            
        except Exception:
            # If player endpoint fails completely, try fallback
            return self._get_song_fallback(videoId)

    def _get_song_fallback(self, videoId: str) -> JsonDict:
        """
        Fallback method to get basic song metadata using 'next' endpoint.
        This works without authentication and is compatible with iOS client.
        """
        try:
            # Use 'next' endpoint which doesn't require authentication
            response = self._send_request("next", {"videoId": videoId})
            
            # Extract metadata from the response
            song_data = self._extract_song_metadata_from_next(response, videoId)
            
            # Create videoDetails structure
            video_details = {
                'videoId': song_data['videoId'],
                'title': song_data['title'],
                'author': song_data['author'],
                'channelId': song_data['channelId'],
                'viewCount': song_data['viewCount'],
                'isLiveContent': song_data['isLiveContent']
            }
            
            # Return in expected get_song format
            return {
                'playabilityStatus': {'status': 'OK'},
                'videoDetails': video_details
            }
            
        except Exception:
            # Last resort - return minimal structure
            return {
                'playabilityStatus': {'status': 'ERROR', 'reason': 'Video not available'},
                'videoDetails': {
                    'videoId': videoId,
                    'title': 'Unknown Title',
                    'author': 'Unknown Artist',
                    'channelId': '',
                    'viewCount': '0',
                    'isLiveContent': False
                }
            }

    def _extract_song_metadata_from_next(self, response: JsonDict, videoId: str) -> JsonDict:
        """Extract song metadata from 'next' endpoint response"""
        song_data = {
            'videoId': videoId,
            'title': 'Unknown Title',
            'author': 'Unknown Artist',
            'channelId': '',
            'viewCount': '0',
            'isLiveContent': False
        }
        
        try:
            # Navigate the response structure
            contents = response.get('contents', {})
            
            # Check for music watch next results (iOS format)
            if 'singleColumnMusicWatchNextResultsRenderer' in contents:
                music_watch = contents['singleColumnMusicWatchNextResultsRenderer']
                
                # Look for tabs or results
                if 'tabbedRenderer' in music_watch:
                    tabbed = music_watch['tabbedRenderer']
                    if 'watchNextTabbedResultsRenderer' in tabbed:
                        watch_tabs = tabbed['watchNextTabbedResultsRenderer']
                        
                        # Look in tabs
                        tabs = watch_tabs.get('tabs', [])
                        for tab in tabs:
                            if 'tabRenderer' in tab:
                                tab_renderer = tab['tabRenderer']
                                if 'content' in tab_renderer:
                                    content = tab_renderer['content']
                                    # Recursively search for metadata in tab content
                                    found_data = self._search_for_metadata_recursive(content, videoId)
                                    if found_data:
                                        song_data.update(found_data)
                                        break
                
                # Also check direct content
                found_data = self._search_for_metadata_recursive(music_watch, videoId)
                if found_data:
                    song_data.update(found_data)
            
            # Check current video endpoint for additional info
            if 'currentVideoEndpoint' in response:
                current_video = response['currentVideoEndpoint']
                if 'watchEndpoint' in current_video:
                    watch_endpoint = current_video['watchEndpoint']
                    if 'videoId' in watch_endpoint:
                        song_data['videoId'] = watch_endpoint['videoId']
        
        except Exception:
            pass  # Return defaults if extraction fails
        
        return song_data

    def _search_for_metadata_recursive(self, data, target_video_id: str, depth: int = 0) -> JsonDict:
        """Recursively search for song metadata in response data"""
        if depth > 5:  # Prevent infinite recursion
            return {}
        
        found = {}
        
        try:
            if isinstance(data, dict):
                # Look for title renderers
                if 'title' in data:
                    title_data = data['title']
                    if isinstance(title_data, dict):
                        if 'runs' in title_data and title_data['runs']:
                            title = title_data['runs'][0].get('text', '')
                            if title:
                                found['title'] = title
                        elif 'simpleText' in title_data:
                            found['title'] = title_data['simpleText']
                
                # Look for author/artist info
                if 'subtitle' in data:
                    subtitle_data = data['subtitle']
                    if isinstance(subtitle_data, dict):
                        if 'runs' in subtitle_data and subtitle_data['runs']:
                            author = subtitle_data['runs'][0].get('text', '')
                            if author:
                                found['author'] = author
                        elif 'simpleText' in subtitle_data:
                            found['author'] = subtitle_data['simpleText']
                
                # Look for navigation endpoints for channel ID
                if 'navigationEndpoint' in data:
                    nav = data['navigationEndpoint']
                    if 'browseEndpoint' in nav:
                        browse = nav['browseEndpoint']
                        if 'browseId' in browse:
                            found['channelId'] = browse['browseId']
                
                # Look for video ID confirmation
                if 'videoId' in data and data['videoId'] == target_video_id:
                    found['videoId'] = data['videoId']
                
                # Look for view count
                if 'viewCountText' in data:
                    view_text = data['viewCountText']
                    if isinstance(view_text, dict) and 'simpleText' in view_text:
                        found['viewCount'] = view_text['simpleText']
                
                # Recursively search nested structures
                for key, value in data.items():
                    if isinstance(value, (dict, list)) and not found.get('title'):
                        nested_found = self._search_for_metadata_recursive(value, target_video_id, depth + 1)
                        if nested_found:
                            found.update(nested_found)
                            if found.get('title'):  # Stop if we found a title
                                break
            
            elif isinstance(data, list):
                for item in data:
                    nested_found = self._search_for_metadata_recursive(item, target_video_id, depth + 1)
                    if nested_found:
                        found.update(nested_found)
                        if found.get('title'):  # Stop if we found a title
                            break
        
        except Exception:
            pass  # Continue silently if extraction fails
        
        return found

    def get_song_related(self, browseId: str) -> JsonList:
        """
        Gets related content for a song. Equivalent to the content
        shown in the "Related" tab of the watch panel.

        :param browseId: The ``related`` key  in the ``get_watch_playlist`` response.

        Example::

            [
              {
                "title": "You might also like",
                "contents": [
                  {
                    "title": "High And Dry",
                    "videoId": "7fv84nPfTH0",
                    "artists": [{
                        "name": "Radiohead",
                        "id": "UCr_iyUANcn9OX_yy9piYoLw"
                      }],
                    "thumbnails": [
                      {
                        "url": "https://lh3.googleusercontent.com/TWWT47cHLv3yAugk4h9eOzQ46FHmXc_g-KmBVy2d4sbg_F-Gv6xrPglztRVzp8D_l-yzOnvh-QToM8s=w60-h60-l90-rj",
                        "width": 60,
                        "height": 60
                      }
                    ],
                    "isExplicit": false,
                    "album": {
                      "name": "The Bends",
                      "id": "MPREb_xsmDKhqhQrG"
                    }
                  }
                ]
              },
              {
                "title": "Recommended playlists",
                "contents": [
                  {
                    "title": "'90s Alternative Rock Hits",
                    "playlistId": "RDCLAK5uy_m_h-nx7OCFaq9AlyXv78lG0AuloqW_NUA",
                    "thumbnails": [...],
                    "description": "Playlist • YouTube Music"
                  }
                ]
              },
              {
                "title": "Similar artists",
                "contents": [
                  {
                    "title": "Noel Gallagher",
                    "browseId": "UCu7yYcX_wIZgG9azR3PqrxA",
                    "subscribers": "302K",
                    "thumbnails": [...]
                  }
                ]
              },
              {
                "title": "Oasis",
                "contents": [
                  {
                    "title": "Shakermaker",
                    "year": "2014",
                    "browseId": "MPREb_WNGQWp5czjD",
                    "thumbnails": [...]
                  }
                ]
              },
              {
                "title": "About the artist",
                "contents": "Oasis were a rock band consisting of Liam Gallagher, Paul ... (full description shortened for documentation)"
              }
            ]
        """
        if not browseId:
            raise YTMusicUserError("Invalid browseId provided.")

        response = self._send_request("browse", {"browseId": browseId})
        sections = nav(response, ["contents", *SECTION_LIST])
        return parse_mixed_content(
            sections,
        )

    @overload
    def get_lyrics(self, browseId: str, timestamps: Literal[False] = False) -> Lyrics | None:
        """overload for mypy only"""

    @overload
    def get_lyrics(self, browseId: str, timestamps: Literal[True] = True) -> Lyrics | TimedLyrics | None:
        """overload for mypy only"""

    def get_lyrics(self, browseId: str, timestamps: bool | None = False) -> Lyrics | TimedLyrics | None:
        """
        Returns lyrics of a song or video. When `timestamps` is set, lyrics are returned with
        timestamps, if available.

        :param browseId: Lyrics browseId obtained from :py:func:`get_watch_playlist` (startswith ``MPLYt...``).
        :param timestamps: Optional. Whether to return bare lyrics or lyrics with timestamps, if available. (Default: `False`)
        :return: Dictionary with song lyrics or ``None``, if no lyrics are found.
            The ``hasTimestamps``-key determines the format of the data.


            Example when `timestamps=False`, or no timestamps are available::

                {
                    "lyrics": "Today is gonna be the day\\nThat they're gonna throw it back to you\\n",
                    "source": "Source: LyricFind",
                    "hasTimestamps": False
                }

            Example when `timestamps` is set to `True` and timestamps are available::

                {
                    "lyrics": [
                        LyricLine(
                            text="I was a liar",
                            start_time=9200,
                            end_time=10630,
                            id=1
                        ),
                        LyricLine(
                            text="I gave in to the fire",
                            start_time=10680,
                            end_time=12540,
                            id=2
                        ),
                    ],
                    "source": "Source: LyricFind",
                    "hasTimestamps": True
                }

        """
        if not browseId:
            raise YTMusicUserError("Invalid browseId provided. This song might not have lyrics.")

        if timestamps:
            # changes and restores the client to get lyrics with timestamps (mobile only)
            with self.as_mobile():
                response = self._send_request("browse", {"browseId": browseId})
        else:
            response = self._send_request("browse", {"browseId": browseId})

        # unpack the response
        lyrics: Lyrics | TimedLyrics
        if timestamps and (data := nav(response, TIMESTAMPED_LYRICS, True)) is not None:
            # we got lyrics with timestamps
            assert isinstance(data, dict)

            if "timedLyricsData" not in data:  # pragma: no cover
                return None

            lyrics = TimedLyrics(
                lyrics=list(map(LyricLine.from_raw, data["timedLyricsData"])),
                source=data.get("sourceMessage"),
                hasTimestamps=True,
            )
        else:
            lyrics_str = nav(
                response, ["contents", *SECTION_LIST_ITEM, *DESCRIPTION_SHELF, *DESCRIPTION], True
            )

            if lyrics_str is None:  # pragma: no cover
                return None

            # Try to get source from footer first (iOS format), then fallback to RUN_TEXT path
            source = nav(response, ["contents", *SECTION_LIST_ITEM, *DESCRIPTION_SHELF, "footer", "runs", 0, "text"], True)
            if source is None:
                source = nav(response, ["contents", *SECTION_LIST_ITEM, *DESCRIPTION_SHELF, *RUN_TEXT], True)

            lyrics = Lyrics(
                lyrics=lyrics_str,
                source=source,
                hasTimestamps=False,
            )

        return cast(Lyrics | TimedLyrics, lyrics)

    def get_basejs_url(self) -> str:
        """
        Extract the URL for the `base.js` script from YouTube Music.

        :return: URL to `base.js`
        """
        response = self._send_get_request(url=YTM_DOMAIN)
        match = re.search(r'jsUrl"\s*:\s*"([^"]+)"', response.text)
        if match is None:
            raise YTMusicError("Could not identify the URL for base.js player.")

        return YTM_DOMAIN + match.group(1)

    def get_signatureTimestamp(self, url: str | None = None) -> int:
        """
        Fetch the `base.js` script from YouTube Music and parse out the
        ``signatureTimestamp`` for use with :py:func:`get_song`.

        :param url: Optional. Provide the URL of the `base.js` script. If this
            isn't specified a call will be made to :py:func:`get_basejs_url`.
        :return: ``signatureTimestamp`` string
        """
        if url is None:
            url = self.get_basejs_url()
        response = self._send_get_request(url=url)
        match = re.search(r"signatureTimestamp[:=](\d+)", response.text)
        if match is None:
            raise YTMusicError("Unable to identify the signatureTimestamp.")

        return int(match.group(1))

    def get_tasteprofile(self) -> JsonDict:
        """
        Fetches suggested artists from taste profile (music.youtube.com/tasteprofile). Must be authenticated.
        Tasteprofile allows users to pick artists to update their recommendations.
        Only returns a list of suggested artists, not the actual list of selected entries

        :return: Dictionary with artist and their selection & impression value

        Example::

            {
                "Drake": {
                    "selectionValue": "tastebuilder_selection=/m/05mt_q"
                    "impressionValue": "tastebuilder_impression=/m/05mt_q"
                }
            }

        """
        self._check_auth()
        response = self._send_request("browse", {"browseId": "FEmusic_tastebuilder"})
        profiles = nav(response, TASTE_PROFILE_ITEMS)

        taste_profiles = {}
        for itemList in profiles:
            for item in itemList["tastebuilderItemListRenderer"]["contents"]:
                artist = nav(item["tastebuilderItemRenderer"], TASTE_PROFILE_ARTIST)[0]["text"]
                taste_profiles[artist] = {
                    "selectionValue": item["tastebuilderItemRenderer"]["selectionFormValue"],
                    "impressionValue": item["tastebuilderItemRenderer"]["impressionFormValue"],
                }
        return taste_profiles

    def set_tasteprofile(self, artists: list[str], taste_profile: JsonDict | None = None) -> None:
        """
        Favorites artists to see more recommendations from the artist.
        Use :py:func:`get_tasteprofile` to see which artists are available to be recommended

        :param artists: A List with names of artists, must be contained in the tasteprofile
        :param taste_profile: tasteprofile result from :py:func:`get_tasteprofile`.
            Pass this if you call :py:func:`get_tasteprofile` anyway to save an extra request.
        :return: None if successful
        """

        if taste_profile is None:
            taste_profile = self.get_tasteprofile()
        formData = {
            "impressionValues": [taste_profile[profile]["impressionValue"] for profile in taste_profile],
            "selectedValues": [],
        }

        for artist in artists:
            if artist not in taste_profile:
                raise YTMusicUserError(f"The artist {artist} was not present in taste!")
            formData["selectedValues"].append(taste_profile[artist]["selectionValue"])

        body = {"browseId": "FEmusic_home", "formData": formData}
        self._send_request("browse", body)

    def _parse_ios_mixed_content(self, results: JsonList) -> JsonList:
        """
        Parse iOS Music format mixed content.
        Handles elementRenderer -> newElement -> musicListItemCarouselModel structure.
        """
        items = []
        
        for section in results:
            if 'elementRenderer' not in section:
                continue
                
            element = section['elementRenderer']
            if 'newElement' not in element:
                continue
                
            new_element = element['newElement']
            if 'model' not in new_element.get('type', {}).get('componentType', {}):
                continue
                
            model = new_element['type']['componentType']['model']
            
            # Handle musicListItemCarouselModel
            if 'musicListItemCarouselModel' in model:
                carousel_model = model['musicListItemCarouselModel']
                
                # Extract title
                if 'header' in carousel_model and 'title' in carousel_model['header']:
                    title = carousel_model['header']['title']
                else:
                    title = 'Quick picks'  # Default title for sections without header
                
                contents = []
                if 'listItems' in carousel_model:
                    for item in carousel_model['listItems']:
                        # Extract song information from iOS format
                        song_data = {
                            'title': item.get('title', ''),
                            'videoId': '',
                            'thumbnails': [],
                            'artists': []
                        }
                        
                        # Extract subtitle for artist info
                        if 'subtitle' in item:
                            subtitle = item['subtitle']
                            # Parse artist info from subtitle - usually in format "Artist • Plays"
                            if ' • ' in subtitle:
                                artist_part = subtitle.split(' • ')[0]
                                song_data['artists'] = [{'name': artist_part.strip()}]
                        
                        # Extract thumbnail
                        if 'thumbnail' in item and 'image' in item['thumbnail']:
                            song_data['thumbnails'] = item['thumbnail']['image'].get('sources', [])
                        
                        # Extract video ID from onTap command
                        if 'onTap' in item and 'innertubeCommand' in item['onTap']:
                            command = item['onTap']['innertubeCommand']
                            if 'watchEndpoint' in command:
                                song_data['videoId'] = command['watchEndpoint'].get('videoId', '')
                        
                        contents.append(song_data)
                
                # Build section result
                section_result = {
                    'title': title,
                    'contents': contents
                }
                items.append(section_result)
            
            # Handle statementBannerModel (promotional banners) if needed
            elif 'statementBannerModel' in model:
                # Skip banners for now
                pass
        
        return items
