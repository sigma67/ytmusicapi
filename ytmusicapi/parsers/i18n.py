from gettext import GNUTranslations
from gettext import gettext as _

from ytmusicapi.navigation import (
    CAROUSEL,
    CAROUSEL_TITLE,
    MMRIR,
    MTRIR,
    NAVIGATION_BROWSE,
    NAVIGATION_BROWSE_ID,
    nav,
)
from ytmusicapi.parsers._utils import i18n
from ytmusicapi.parsers.browsing import (
    parse_album,
    parse_content_list,
    parse_playlist,
    parse_related_artist,
    parse_single,
    parse_video,
)
from ytmusicapi.parsers.podcasts import parse_episode, parse_podcast
from ytmusicapi.type_alias import JsonDict, JsonList


class Parser:
    def __init__(self, language: GNUTranslations) -> None:
        self.lang = language

    @i18n
    def get_search_result_types(self) -> list[str]:
        return [
            _("album"),
            _("artist"),
            _("playlist"),
            _("song"),
            _("video"),
            _("station"),
            _("profile"),
            _("podcast"),
            _("episode"),
        ]

    @i18n
    def get_api_result_types(self) -> list[str]:
        return [
            _("single"),
            _("ep"),
            *self.get_search_result_types(),
        ]

    @i18n
    def parse_channel_contents(self, results: JsonList) -> JsonDict:
        categories = [
            ("albums", _("albums"), parse_album, MTRIR),
            ("singles", _("singles & eps"), parse_single, MTRIR),
            ("shows", _("shows"), parse_album, MTRIR),
            ("videos", _("videos"), parse_video, MTRIR),
            ("playlists", _("playlists"), parse_playlist, MTRIR),
            ("related", _("related"), parse_related_artist, MTRIR),
            ("episodes", _("episodes"), parse_episode, MMRIR),
            ("podcasts", _("podcasts"), parse_podcast, MTRIR),
        ]
        artist: JsonDict = {}
        for category, category_local, category_parser, category_key in categories:
            data = [
                r["musicCarouselShelfRenderer"]
                for r in results
                if "musicCarouselShelfRenderer" in r
                and nav(r, CAROUSEL + CAROUSEL_TITLE)["text"].lower() == category_local.lower()
            ]
            if len(data) > 0:
                artist[category] = {"browseId": None, "results": []}
                if "navigationEndpoint" in nav(data[0], CAROUSEL_TITLE):
                    artist[category]["browseId"] = nav(data[0], CAROUSEL_TITLE + NAVIGATION_BROWSE_ID)
                    artist[category]["params"] = nav(
                        data[0], CAROUSEL_TITLE + NAVIGATION_BROWSE + ["params"], True
                    )

                artist[category]["results"] = parse_content_list(
                    data[0]["contents"], category_parser, key=category_key
                )

        return artist
