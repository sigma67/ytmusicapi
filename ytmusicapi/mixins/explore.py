from ytmusicapi.parsers.explore import *


class ExploreMixin:
    def get_mood_categories(self) -> Dict:
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
        sections = {}
        response = self._send_request('browse', {'browseId': 'FEmusic_moods_and_genres'})
        for section in nav(response, SINGLE_COLUMN_TAB + SECTION_LIST):
            title = nav(section, GRID + ['header', 'gridHeaderRenderer'] + TITLE_TEXT)
            sections[title] = []
            for category in nav(section, GRID_ITEMS):
                sections[title].append({
                    "title": nav(category, CATEGORY_TITLE),
                    "params": nav(category, CATEGORY_PARAMS)
                })

        return sections

    def get_mood_playlists(self, params: str) -> List[Dict]:
        """
        Retrieve a list of playlists for a given "Moods & Genres" category.

        :param params: params obtained by :py:func:`get_mood_categories`
        :return: List of playlists in the format of :py:func:`get_library_playlists`

        """
        playlists = []
        response = self._send_request('browse', {
            'browseId': 'FEmusic_moods_and_genres_category',
            'params': params
        })
        for section in nav(response, SINGLE_COLUMN_TAB + SECTION_LIST):
            path = []
            if 'gridRenderer' in section:
                path = GRID_ITEMS
            elif 'musicCarouselShelfRenderer' in section:
                path = CAROUSEL_CONTENTS
            elif 'musicImmersiveCarouselShelfRenderer' in section:
                path = ['musicImmersiveCarouselShelfRenderer', 'contents']
            if len(path):
                results = nav(section, path)
                playlists += parse_content_list(results, parse_playlist)

        return playlists

    def get_charts(self, country: str = 'ZZ') -> Dict:
        """
        Get latest charts data from YouTube Music.

        :param country: ISO 3166-1 Alpha-2 country code
        :return: Dictionary containing chart songs (only if authenticated), chart videos, chart artists and
            trending videos.
        """
        body = {'browseId': 'FEmusic_charts'}
        if country:
            body['formData'] = {'selectedValues': [country]}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        charts = {'countries': {}}
        menu = nav(
            results[0], MUSIC_SHELF + [
                'subheaders', 0, 'musicSideAlignedItemRenderer', 'startItems', 0,
                'musicSortFilterButtonRenderer'
            ])
        charts['countries']['selected'] = nav(menu, TITLE)
        charts['countries']['options'] = list(
            filter(None, [
                nav(m, ['payload', 'musicFormBooleanChoice', 'opaqueToken'], True)
                for m in nav(response, FRAMEWORK_MUTATIONS)
            ]))
        charts_categories = ['videos', 'artists']

        has_songs = bool(self.auth)
        has_trending = bool(5 - len(results) - has_songs)
        if has_songs:
            charts_categories.insert(0, 'songs')
        if has_trending:
            charts_categories.append('trending')

        parse_chart = lambda i, parse_func, key: parse_content_list(
            nav(results[i + has_songs], CAROUSEL_CONTENTS), parse_func, key)
        for i, c in enumerate(charts_categories):
            charts[c] = {
                'playlist': nav(results[1 + i], CAROUSEL + CAROUSEL_TITLE + NAVIGATION_BROWSE_ID,
                                True)
            }

        if has_songs:
            charts['songs'] = {
                'items': parse_chart(0, parse_chart_song, MRLIR)
            }
        charts['videos']['items'] = parse_chart(1, parse_video, MTRIR)
        charts['artists']['items'] = parse_chart(2, parse_chart_artist, MRLIR)
        if has_trending:
            charts['trending']['items'] = parse_chart(3, parse_chart_trending, MRLIR)

        return charts
