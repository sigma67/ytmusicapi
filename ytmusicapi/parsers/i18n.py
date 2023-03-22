from typing import List, Dict

from ytmusicapi.navigation import nav, CAROUSEL, CAROUSEL_TITLE, NAVIGATION_BROWSE_ID
from ytmusicapi.parsers._utils import i18n
from ytmusicapi.parsers.browsing import parse_album, parse_single, parse_video, parse_playlist, parse_related_artist, \
    parse_content_list


class Parser:

    def __init__(self, language):
        self.lang = language

    @i18n
    def get_search_result_types(self):
        return [_('artist'), _('playlist'), _('song'), _('video'), _('station')]

    @i18n
    def parse_artist_contents(self, results: List) -> Dict:
        categories = ['albums', 'singles', 'videos', 'playlists', 'related']
        categories_local = [_('albums'), _('singles'), _('videos'), _('playlists'), _('related')]
        categories_parser = [
            parse_album, parse_single, parse_video, parse_playlist, parse_related_artist
        ]
        artist = {}
        for i, category in enumerate(categories):
            data = [
                r['musicCarouselShelfRenderer'] for r in results
                if 'musicCarouselShelfRenderer' in r
                and nav(r, CAROUSEL + CAROUSEL_TITLE)['text'].lower() == categories_local[i]
            ]
            if len(data) > 0:
                artist[category] = {'browseId': None, 'results': []}
                if 'navigationEndpoint' in nav(data[0], CAROUSEL_TITLE):
                    artist[category]['browseId'] = nav(data[0],
                                                       CAROUSEL_TITLE + NAVIGATION_BROWSE_ID)
                    if category in ['albums', 'singles', 'playlists']:
                        artist[category]['params'] = nav(
                            data[0],
                            CAROUSEL_TITLE)['navigationEndpoint']['browseEndpoint']['params']

                artist[category]['results'] = parse_content_list(data[0]['contents'],
                                                                 categories_parser[i])

        return artist
