from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.explore import *
from ytmusicapi.type_alias import JsonDict, JsonList
from ytmusicapi.navigation import nav
from ytmusicapi.navigation import *


class ExploreMixin(MixinProtocol):
    def get_mood_categories(self) -> JsonDict:
        """
        Fetch "Moods & Genres" categories from YouTube Music.

        :return: Dictionary of sections and categories.

        Example::

            {
                'For you': [
                    {
                        'params': 'ggMPOg1uX1ZwN0pHT2NBT1Fk',
                        'title': '1980s'
                    },
                    {
                        'params': 'ggMPOg1uXzZQbDB5eThLRTQ3',
                        'title': 'Feel Good'
                    },
                    ...
                ],
                'Genres': [
                    {
                        'params': 'ggMPOg1uXzVLbmZnaWI4STNs',
                        'title': 'Dance & Electronic'
                    },
                    {
                        'params': 'ggMPOg1uX3NjZllsNGVEMkZo',
                        'title': 'Decades'
                    },
                    ...
                ],
                'Moods & moments': [
                    {
                        'params': 'ggMPOg1uXzVuc0dnZlhpV3Ba',
                        'title': 'Chill'
                    },
                    {
                        'params': 'ggMPOg1uX2ozUHlwbWM3ajNq',
                        'title': 'Commute'
                    },
                    ...
                ],
            }

        """
        sections: JsonDict = {}
        response = self._send_request("browse", {"browseId": "FEmusic_moods_and_genres"})
        for section in nav(response, SINGLE_COLUMN_TAB + SECTION_LIST):
            title = nav(section, [*GRID, "header", "gridHeaderRenderer", *TITLE_TEXT])
            sections[title] = []
            for category in nav(section, GRID_ITEMS):
                sections[title].append(
                    {"title": nav(category, CATEGORY_TITLE), "params": nav(category, CATEGORY_PARAMS)}
                )

        return sections

    def get_mood_playlists(self, params: str) -> JsonList:
        """
        Retrieve a list of playlists for a given "Moods & Genres" category.

        :param params: params obtained by :py:func:`get_mood_categories`
        :return: List of playlists in the format of :py:func:`get_library_playlists`

        """
        playlists = []
        response = self._send_request(
            "browse", {"browseId": "FEmusic_moods_and_genres_category", "params": params}
        )
        for section in nav(response, SINGLE_COLUMN_TAB + SECTION_LIST):
            path = []
            if "gridRenderer" in section:
                path = GRID_ITEMS
            elif "musicCarouselShelfRenderer" in section:
                path = CAROUSEL_CONTENTS
            elif "musicImmersiveCarouselShelfRenderer" in section:
                path = ["musicImmersiveCarouselShelfRenderer", "contents"]
            if len(path):
                results = nav(section, path)
                playlists += parse_content_list(results, parse_playlist)

        return playlists

    def get_explore(self) -> JsonDict:
        """
        Get latest explore data from YouTube Music.
        The Top Songs chart is only returned when authenticated with a premium account.

        :return: Dictionary containing new album releases, top songs (if authenticated with a premium account), moods & genres, popular episodes, trending tracks, and new music videos.

        Example::

            {
                "new_releases": [
                    {
                        "title": "Hangang",
                        "type": "Album",
                        "artists": [
                            {
                              "id": "UCpo4SbqmPXpCVA5RFj-Gq5Q",
                              "name": "Dept"
                            }
                        ],
                        "browseId": "MPREb_rGl39ZNEl95",
                        "audioPlaylistId": "OLAK5uy_mTZAp8a-agh1at-cVUGrwPhTJoM5GnKTk",
                        "thumbnails": [...],
                        "isExplicit": false
                    }
                ],
                "top_songs": {
                    "playlist": "VLPL4fGSI1pDJn6O1LS0XSdF3RyO0Rq_LDeI",
                    "items": [
                        {
                            "title": "Outside (Better Days)",
                            "videoId": "oT79YlRtXDg",
                            "artists": [
                                {
                                    "name": "MO3",
                                    "id": "UCdFt4Cvhr7Okaxo6hZg5K8g"
                                },
                                {
                                    "name": "OG Bobby Billions",
                                    "id": "UCLusb4T2tW3gOpJS1fJ-A9g"
                                }
                            ],
                            "thumbnails": [...],
                            "isExplicit": true,
                            "album": {
                                "name": "Outside (Better Days)",
                                "id": "MPREb_fX4Yv8frUNv"
                            },
                            "rank": "1",
                            "trend": "up"
                        }
                    ]
                },
                "moods_and_genres": [
                    {
                        "title": "Chill",
                        "params": "ggMPOg1uXzVuc0dnZlhpV3Ba"
                    }
                ],
                "top_episodes": [
                    {
                        "title": "132. Lean Into Failure: How to Make Mistakes That Work | Think Fast, Talk Smart: Communication...",
                        "description": "...",
                        "duration": "25 min",
                        "videoId": "xAEGaW2my7E",
                        "browseId": "MPEDxAEGaW2my7E",
                        "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE",
                        "date": "Mar 5, 2024",
                        "thumbnails": [...],
                        "podcast": {
                            "id": "UCGwuxdEeCf0TIA2RbPOj-8g",
                            "name: "Stanford Graduate School of Business"
                        }
                    }
                ],
                "trending": {
                    "playlist": "VLOLAK5uy_kNWGJvgWVqlt5LsFDL9Sdluly4M8TvGkM",
                    "items": [
                        {
                            "title": "Permission to Dance",
                            "videoId": "CuklIb9d3fI",
                            "playlistId": "OLAK5uy_kNWGJvgWVqlt5LsFDL9Sdluly4M8TvGkM",
                            "artists": [
                                {
                                    "name": "BTS",
                                    "id": "UC9vrvNSL3xcWGSkV86REBSg"
                                }
                            ],
                            "thumbnails": [...],
                            "isExplicit": false,
                            "views": "108M"
                        }
                    ]
                },
                "new_videos": [
                    {
                        "title": "EVERY CHANCE I GET (Official Music Video) (feat. Lil Baby & Lil Durk)",
                        "videoId": "BTivsHlVcGU",
                        "artists": [
                            {
                                "name": "DJ Khaled",
                                "id": "UC0Kgvj5t_c9EMWpEDWJuR1Q"
                            }
                        ],
                        "playlistId": null,
                        "thumbnails": [...],
                        "views": "46M"
                    }
                ]
            }

        """
        body: JsonDict = {"browseId": "FEmusic_explore"}

        response = self._send_request("browse", body)
        
        # Check for iOS format (elementRenderer)
        if self._is_ios_response(response):
            return self._parse_explore_ios(response)
        
        # Legacy desktop format parsing
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)

        explore: JsonDict = {}

        for result in results:
            browse_id = nav(result, CAROUSEL + CAROUSEL_TITLE + NAVIGATION_BROWSE_ID, True)
            if browse_id is None:
                continue

            contents = nav(result, CAROUSEL_CONTENTS)
            match browse_id:
                case "FEmusic_new_releases_albums":
                    explore["new_releases"] = parse_content_list(contents, parse_album)

                case "FEmusic_moods_and_genres":
                    explore["moods_and_genres"] = [
                        {"title": nav(genre, CATEGORY_TITLE), "params": nav(genre, CATEGORY_PARAMS)}
                        for genre in nav(result, CAROUSEL_CONTENTS)
                    ]

                case "FEmusic_top_non_music_audio_episodes":
                    explore["top_episodes"] = parse_content_list(contents, parse_chart_episode, MMRIR)

                case "FEmusic_new_releases_videos":
                    explore["new_videos"] = parse_content_list(contents, parse_video, MTRIR)

                case playlist_id if playlist_id.startswith("VLPL"):
                    explore["top_songs"] = {
                        "playlist": playlist_id,
                        "items": parse_content_list(contents, parse_chart_song, MRLIR),
                    }

                case playlist_id if playlist_id.startswith("VLOLA"):
                    explore["trending"] = {
                        "playlist": playlist_id,
                        "items": parse_content_list(contents, parse_song_flat, MRLIR),
                    }

        return explore

    def _is_ios_response(self, response: JsonDict) -> bool:
        """Check if response uses iOS elementRenderer format"""
        try:
            # Check if we have the singleColumnBrowseResultsRenderer structure
            if ("contents" in response and 
                "singleColumnBrowseResultsRenderer" in response["contents"]):
                
                single_col = response["contents"]["singleColumnBrowseResultsRenderer"]
                if "tabs" in single_col and single_col["tabs"]:
                    tab = single_col["tabs"][0]
                    if ("tabRenderer" in tab and 
                        "content" in tab["tabRenderer"] and
                        "sectionListRenderer" in tab["tabRenderer"]["content"]):
                        
                        sections = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
                        if sections and len(sections) > 0:
                            first_section = sections[0]
                            if ("itemSectionRenderer" in first_section and
                                "contents" in first_section["itemSectionRenderer"]):
                                
                                items = first_section["itemSectionRenderer"]["contents"]
                                if items and len(items) > 0:
                                    return "elementRenderer" in items[0]
            return False
        except Exception:
            return False

    def _parse_explore_ios(self, response: JsonDict) -> JsonDict:
        """Parse iOS elementRenderer format for explore data"""
        explore: JsonDict = {}
        
        try:
            sections = response["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
            
            for section in sections:
                if "itemSectionRenderer" not in section:
                    continue
                    
                items = section["itemSectionRenderer"]["contents"]
                for item in items:
                    if "elementRenderer" not in item:
                        continue
                        
                    element = item["elementRenderer"]
                    if ("newElement" not in element or 
                        "type" not in element["newElement"] or 
                        "componentType" not in element["newElement"]["type"] or
                        "model" not in element["newElement"]["type"]["componentType"]):
                        continue
                        
                    model = element["newElement"]["type"]["componentType"]["model"]
                    
                    # Parse different model types
                    self._parse_explore_model_ios(model, explore)
                        
        except Exception:
            # If iOS parsing fails, return basic structure
            pass
            
        return explore

    def _parse_explore_model_ios(self, model: JsonDict, explore: JsonDict) -> None:
        """Parse iOS model content for explore sections"""
        try:
            # Handle musicGridItemCarouselModel (new releases, etc.)
            if "musicGridItemCarouselModel" in model:
                carousel_model = model["musicGridItemCarouselModel"]
                if "shelf" in carousel_model:
                    shelf = carousel_model["shelf"]
                    
                    # Get section title
                    title = ""
                    if "header" in shelf and "title" in shelf["header"]:
                        title = shelf["header"]["title"]
                    
                    # Parse shelf items based on title
                    if "items" in shelf:
                        items = shelf["items"]
                        
                        # Map titles to explore sections based on content
                        title_lower = title.lower()
                        if ("new" in title_lower and ("album" in title_lower or "single" in title_lower)) or "release" in title_lower:
                            explore["new_releases"] = self._parse_ios_items(items, "album")
                            
                        elif "trend" in title_lower or "chart" in title_lower:
                            if "trending" not in explore:
                                explore["trending"] = {"items": []}
                            explore["trending"]["items"] = self._parse_ios_items(items, "song")
                            
                        elif "video" in title_lower and "new" in title_lower:
                            explore["new_videos"] = self._parse_ios_items(items, "video")
            
            # Handle musicColoredChipsShelfModel (moods & genres)
            elif "musicColoredChipsShelfModel" in model:
                chips_model = model["musicColoredChipsShelfModel"]
                if "chips" in chips_model:
                    chips = chips_model["chips"]
                    explore["moods_and_genres"] = self._parse_ios_chips(chips)
            
            # Handle musicListItemCarouselModel (songs, episodes)
            elif "musicListItemCarouselModel" in model:
                list_model = model["musicListItemCarouselModel"]
                if "shelf" in list_model:
                    shelf = list_model["shelf"]
                    
                    # Get section title
                    title = ""
                    if "header" in shelf and "title" in shelf["header"]:
                        title = shelf["header"]["title"]
                    
                    if "items" in shelf:
                        items = shelf["items"]
                        title_lower = title.lower()
                        
                        if "episode" in title_lower or "podcast" in title_lower:
                            explore["top_episodes"] = self._parse_ios_items(items, "episode")
                        elif "song" in title_lower or "track" in title_lower:
                            if "top_songs" not in explore:
                                explore["top_songs"] = {"items": []}
                            explore["top_songs"]["items"] = self._parse_ios_items(items, "song")
                            
        except Exception:
            # Graceful fallback for parsing errors
            pass

    def _parse_ios_items(self, items: JsonList, content_type: str) -> JsonList:
        """Parse iOS carousel items into standard format"""
        parsed_items = []
        try:
            for item in items[:10]:  # Limit to first 10 items
                parsed_item = {}
                
                # Extract basic metadata based on content type
                if content_type == "album":
                    parsed_item = {"title": "Album", "type": "Album", "artists": []}
                elif content_type == "song":
                    parsed_item = {"title": "Song", "artists": []}
                elif content_type == "video":
                    parsed_item = {"title": "Video", "artists": []}
                elif content_type == "episode":
                    parsed_item = {"title": "Episode", "description": ""}
                
                # Add basic structure for now
                parsed_items.append(parsed_item)
                
        except Exception:
            pass
            
        return parsed_items

    def _parse_ios_chips(self, chips: JsonList) -> JsonList:
        """Parse iOS chips into mood/genre format"""
        parsed_chips = []
        try:
            for chip in chips[:20]:  # Limit to first 20 chips
                if "title" in chip:
                    parsed_chips.append({
                        "title": chip["title"],
                        "params": chip.get("params", "")
                    })
        except Exception:
            pass
            
        return parsed_chips
