from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.explore import *
from ytmusicapi.type_alias import JsonDict


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
            ("videos", parse_chart_playlist, MTRIR),
            *([("genres", parse_chart_playlist, MTRIR)] if country == "US" else []),
            ("artists", parse_chart_artist, MRLIR),
        ]

        # use result length to determine if the daily/weekly chart categories are present
        # could also be done via an is_premium attribute on YTMusic instance
        if (len(results) - 1) > len(charts_categories):
            # daily and weekly replace the "videos" playlist carousel
            charts_categories = [
                ("daily", parse_chart_playlist, MTRIR),
                ("weekly", parse_chart_playlist, MTRIR),
            ] + charts_categories[1:]

        for i, (name, parse_func, key) in enumerate(charts_categories):
            charts[name] = parse_content_list(nav(results[1 + i], CAROUSEL_CONTENTS), parse_func, key)

        return charts
