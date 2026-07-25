from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.explore import *
from ytmusicapi.type_alias import JsonDict, JsonList

# extra playlist carousel some countries return between the video charts and the artists
COUNTRY_EXTRA_CATEGORY = {"US": "genres", "IN": "languages"}


def is_playlist_carousel(contents: JsonList) -> bool:
    """chart playlists are the only carousel items linking to a "VL" playlist"""
    browse_id = nav(contents[0], [MTRIR, *TITLE, *NAVIGATION_BROWSE_ID], True)
    return bool(browse_id and browse_id.startswith("VL"))


def is_artist_carousel(contents: JsonList) -> bool:
    return MRLIR in contents[0]


class ChartsMixin(MixinProtocol):
    def get_charts(self, country: str = "ZZ") -> JsonDict:
        """
        Get latest charts data from YouTube Music: Artists and playlists of top videos.
        Unauthenticated requests return unranked Artists with "rank" and "trend" set to None.
        US charts have an extra Genres section, IN charts an extra Languages section.

        :param country: ISO 3166-1 Alpha-2 country code. Default: ``ZZ`` = Global
        :return: Dictionary containing chart video playlists (with separate daily/weekly charts if authenticated with a premium account),
            chart genres (US-only, not returned by every response), chart languages (IN-only) and chart artists.

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

        # carousels carry no machine-readable identity, so recognize them by their contents;
        # anything else (some regions add an album chart) is ignored instead of shifting the
        # categories that come after it
        carousels = [c for section in results[1:] if (c := nav(section, CAROUSEL_CONTENTS, True))]
        playlist_carousels = [c for c in carousels if is_playlist_carousel(c)]
        artist_carousels = [c for c in carousels if is_artist_carousel(c)]

        playlist_names = ["videos"]
        if country in COUNTRY_EXTRA_CATEGORY:
            playlist_names.append(COUNTRY_EXTRA_CATEGORY[country])
        # premium sessions get daily and weekly carousels instead of a single "videos" one
        if len(playlist_carousels) > len(playlist_names):
            playlist_names = ["daily", "weekly", *playlist_names[1:]]

        for name, contents in zip(playlist_names, playlist_carousels):
            charts[name] = parse_content_list(contents, parse_chart_playlist, MTRIR)

        if artist_carousels:
            charts["artists"] = parse_content_list(artist_carousels[0], parse_chart_artist, MRLIR)

        return charts
