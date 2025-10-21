from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.navigation import (
    CAROUSEL_CONTENTS,
    FRAMEWORK_MUTATIONS,
    MRLIR,
    MTRIR,
    MUSIC_SHELF,
    SECTION_LIST,
    SINGLE_COLUMN_TAB,
    TITLE,
    nav,
)
from ytmusicapi.parsers.explore import parse_chart_artist, parse_chart_playlist
from ytmusicapi.parsers.i18n import parse_content_list
from ytmusicapi.type_alias import JsonDict


def is_ios_response(response: JsonDict) -> bool:
    """
    Detect if the response is from iOS client based on structure.
    iOS responses use singleColumnBrowseResultsRenderer instead of twoColumn.
    """
    return "singleColumnBrowseResultsRenderer" in response.get("contents", {})


class ChartsMixin(MixinProtocol):
    def get_charts(self, country: str = "ZZ") -> JsonDict:
        """
        Get latest charts data from YouTube Music: Artists and playlists of top videos.
        US charts have an extra Genres section with some Genre charts.

        :param country: ISO 3166-1 Alpha-2 country code. Default: ``ZZ`` = Global
        :return: Dictionary containing chart video playlists (with separate daily/weekly charts if authenticated with a premium account),
            chart genres (US-only), and chart artists.

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
                "videos": [
                    {
                        "title": "Daily Top Music Videos - United States",
                        "playlistId": "PL4fGSI1pDJn61unMfmrUSz68RT8IFFnks",
                        "thumbnails": []
                    }
                ],
                "artists": [
                    {
                        "title": "YoungBoy Never Broke Again",
                        "browseId": "UCR28YDxjDE3ogQROaNdnRbQ",
                        "subscribers": "9.62M",
                        "thumbnails": [],
                        "rank": "1",
                        "trend": "neutral"
                    }
                ],
                "genres": [
                    {
                        "title": "Top 50 Pop Music Videos United States",
                        "playlistId": "PL4fGSI1pDJn77aK7sAW2AT0oOzo5inWY8",
                        "thumbnails": []
                    }
                ]
            }

        """
        body: JsonDict = {"browseId": "FEmusic_charts"}
        if country:
            body["formData"] = {"selectedValues": [country]}

        response = self._send_request("browse", body)
        
        # Detect iOS response and use appropriate parsers
        if is_ios_response(response):
            chart_playlist_parser = self._parse_chart_playlist_ios
            chart_artist_parser = self._parse_chart_artist_ios
        else:
            chart_playlist_parser = parse_chart_playlist
            chart_artist_parser = parse_chart_artist
            
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

        charts_categories = [
            ("videos", chart_playlist_parser, MTRIR),
            *([("genres", chart_playlist_parser, MTRIR)] if country == "US" else []),
            ("artists", chart_artist_parser, MRLIR),
        ]

        # use result length to determine if the daily/weekly chart categories are present
        # could also be done via an is_premium attribute on YTMusic instance
        if (len(results) - 1) > len(charts_categories):
            # daily and weekly replace the "videos" playlist carousel
            charts_categories = [
                ("daily", chart_playlist_parser, MTRIR),
                ("weekly", chart_playlist_parser, MTRIR),
            ] + charts_categories[1:]

        for i, (name, parse_func, key) in enumerate(charts_categories):
            try:
                # Try desktop format first
                charts[name] = parse_content_list(nav(results[1 + i], CAROUSEL_CONTENTS), parse_func, key)
            except (KeyError, TypeError):
                # Handle iOS elementRenderer format
                result_item = results[1 + i]
                if "elementRenderer" in result_item:
                    # Extract content from iOS elementRenderer structure
                    element = result_item["elementRenderer"]["newElement"]
                    if "type" in element and "componentType" in element["type"]:
                        model_data = element["type"]["componentType"].get("model", {})
                        if "musicListItemCarouselModel" in model_data:
                            carousel_model = model_data["musicListItemCarouselModel"]
                            # Extract content items from carousel model
                            content_items = carousel_model.get("content", [])
                            charts[name] = parse_content_list(content_items, parse_func, key)
                        else:
                            charts[name] = []
                    else:
                        charts[name] = []
                else:
                    charts[name] = []

        return charts

    def _parse_chart_playlist_ios(self, item: JsonDict) -> JsonDict:
        """Parse chart playlist item from iOS response format"""
        # Extract basic playlist information from iOS format
        result = {}
        
        # Try to get title from various possible paths
        if "title" in item:
            result["title"] = item["title"]
        elif "flexColumns" in item:
            for col in item["flexColumns"]:
                if "text" in col.get("text", {}):
                    if "runs" in col["text"]:
                        result["title"] = col["text"]["runs"][0]["text"]
                        break
                    else:
                        result["title"] = col["text"]["simpleText"]
                        break
        
        # Try to get playlist ID from navigation command
        nav_command = item.get("onTap", {}).get("innertubeCommand", {})
        if "watchPlaylistEndpoint" in nav_command:
            result["playlistId"] = nav_command["watchPlaylistEndpoint"]["playlistId"]
        elif "browseEndpoint" in nav_command:
            result["browseId"] = nav_command["browseEndpoint"]["browseId"]
        
        # Get thumbnails if available
        thumbnail_data = item.get("thumbnail", {})
        if "image" in thumbnail_data:
            result["thumbnails"] = thumbnail_data["image"].get("sources", [])
        elif "thumbnails" in thumbnail_data:
            result["thumbnails"] = thumbnail_data["thumbnails"]
        else:
            result["thumbnails"] = []
        
        return result

    def _parse_chart_artist_ios(self, item: JsonDict) -> JsonDict:
        """Parse chart artist item from iOS response format"""
        result = {}
        
        # Get artist title
        if "title" in item:
            result["title"] = item["title"]
        elif "flexColumns" in item and len(item["flexColumns"]) > 0:
            first_col = item["flexColumns"][0]
            if "text" in first_col and "runs" in first_col["text"]:
                result["title"] = first_col["text"]["runs"][0]["text"]
        
        # Get subscriber count
        if "subtitle" in item:
            result["subscribers"] = item["subtitle"]
        elif "flexColumns" in item and len(item["flexColumns"]) > 1:
            second_col = item["flexColumns"][1]
            if "text" in second_col:
                if "runs" in second_col["text"]:
                    result["subscribers"] = second_col["text"]["runs"][0]["text"]
                else:
                    result["subscribers"] = second_col["text"]["simpleText"]
        
        # Get browse ID for artist
        nav_command = item.get("onTap", {}).get("innertubeCommand", {})
        if "browseEndpoint" in nav_command:
            result["browseId"] = nav_command["browseEndpoint"]["browseId"]
        
        # Get thumbnails
        thumbnail_data = item.get("thumbnail", {})
        if "image" in thumbnail_data:
            result["thumbnails"] = thumbnail_data["image"].get("sources", [])
        elif "thumbnails" in thumbnail_data:
            result["thumbnails"] = thumbnail_data["thumbnails"]
        else:
            result["thumbnails"] = []
        
        # Get ranking data if available
        ranking = item.get("rankingBadgeData", {})
        if ranking:
            result["rank"] = ranking.get("text", "")
            # Determine trend from icon
            icon = ranking.get("iconName", "")
            if "up" in icon:
                result["trend"] = "up"
            elif "down" in icon:
                result["trend"] = "down"
            else:
                result["trend"] = "neutral"
        
        return result
