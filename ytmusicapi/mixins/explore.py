from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.explore import *
from ytmusicapi.type_alias import JsonDict, JsonList


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
                        "items": parse_content_list(contents, parse_trending_song, MRLIR),
                    }

        return explore
