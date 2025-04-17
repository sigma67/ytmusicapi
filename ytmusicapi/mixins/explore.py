from collections.abc import Callable
from typing import Any

from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.explore import *
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncDictType


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

    def get_charts(self, country: str = "ZZ") -> JsonDict:
        """
        Get latest charts data from YouTube Music: Top songs, top videos, top artists and top trending videos.
        Global charts have no Trending section, US charts have an extra Genres section with some Genre charts.

        :param country: ISO 3166-1 Alpha-2 country code. Default: ``ZZ`` = Global
        :return: Dictionary containing chart songs (only if authenticated with premium account),
            chart videos, chart artists and trending videos.

        Example::

            {
                "countries": {
                    "selected": {
                        "text": "United States"
                    },
                    "options": ["DE",
                        "ZZ",
                        "ZW"]
                },
                "songs": {
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
                "videos": {
                    "playlist": "VLPL4fGSI1pDJn69On1f-8NAvX_CYlx7QyZc",
                    "items": [
                        {
                            "title": "EVERY CHANCE I GET (Official Music Video) (feat. Lil Baby & Lil Durk)",
                            "videoId": "BTivsHlVcGU",
                            "playlistId": "PL4fGSI1pDJn69On1f-8NAvX_CYlx7QyZc",
                            "thumbnails": [],
                            "views": "46M"
                        }
                    ]
                },
                "artists": {
                    "playlist": null,
                    "items": [
                        {
                            "title": "YoungBoy Never Broke Again",
                            "browseId": "UCR28YDxjDE3ogQROaNdnRbQ",
                            "subscribers": "9.62M",
                            "thumbnails": [],
                            "rank": "1",
                            "trend": "neutral"
                        }
                    ]
                },
                "genres": [
                    {
                        "title": "Top 50 Pop Music Videos United States",
                        "playlistId": "PL4fGSI1pDJn77aK7sAW2AT0oOzo5inWY8",
                        "thumbnails": []
                    }
                ],
                "trending": {
                    "playlist": "VLPLrEnWoR732-DtKgaDdnPkezM_nDidBU9H",
                    "items": [
                        {
                            "title": "Permission to Dance",
                            "videoId": "CuklIb9d3fI",
                            "playlistId": "PLrEnWoR732-DtKgaDdnPkezM_nDidBU9H",
                            "artists": [
                                {
                                    "name": "BTS",
                                    "id": "UC9vrvNSL3xcWGSkV86REBSg"
                                }
                            ],
                            "thumbnails": [],
                            "views": "108M"
                        }
                    ]
                }
            }

        """
        body: JsonDict = {"browseId": "FEmusic_charts"}
        if country:
            body["formData"] = {"selectedValues": [country]}

        response = self._send_request("browse", body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        charts: JsonDict = {"countries": {}}
        menu = nav(
            results[0],
            [
                *MUSIC_SHELF,
                "subheaders",
                0,
                "musicSideAlignedItemRenderer",
                "startItems",
                0,
                "musicSortFilterButtonRenderer",
            ],
        )
        charts["countries"]["selected"] = nav(menu, TITLE)
        charts["countries"]["options"] = list(
            filter(
                None,
                [
                    nav(m, ["payload", "musicFormBooleanChoice", "opaqueToken"], True)
                    for m in nav(response, FRAMEWORK_MUTATIONS)
                ],
            )
        )
        charts_categories = ["videos", "artists"]

        has_genres = country == "US"
        has_trending = country != "ZZ"

        # use result length to determine if songs category is present
        # could also be done via an is_premium attribute on YTMusic instance
        has_songs = (len(results) - 1) > (len(charts_categories) + has_genres + has_trending)

        if has_songs:
            charts_categories.insert(0, "songs")
        if has_genres:
            charts_categories.append("genres")
        if has_trending:
            charts_categories.append("trending")

        parse_chart: Callable[[int, ParseFuncDictType, str], list[dict[str, Any]]] = (
            lambda index, parse_func, key: parse_content_list(
                nav(results[index + has_songs], CAROUSEL_CONTENTS), parse_func, key
            )
        )
        for i, c in enumerate(charts_categories):
            charts[c] = {
                "playlist": nav(results[1 + i], CAROUSEL + CAROUSEL_TITLE + NAVIGATION_BROWSE_ID, True)
            }

        if has_songs:
            charts["songs"].update({"items": parse_chart(0, parse_chart_song, MRLIR)})

        charts["videos"]["items"] = parse_chart(1, parse_video, MTRIR)
        charts["artists"]["items"] = parse_chart(2, parse_chart_artist, MRLIR)

        if has_genres:
            charts["genres"] = parse_chart(3, parse_playlist, MTRIR)

        if has_trending:
            charts["trending"]["items"] = parse_chart(3 + has_genres, parse_chart_trending, MRLIR)

        return charts
