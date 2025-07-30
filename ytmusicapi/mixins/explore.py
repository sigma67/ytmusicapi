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
