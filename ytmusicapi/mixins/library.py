from ytmusicapi.helpers import *
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.library import *
from ytmusicapi.parsers.playlists import *


class LibraryMixin:
    def get_library_playlists(self, limit: int = 25) -> List[Dict]:
        """
        Retrieves the playlists in the user's library.

        :param limit: Number of playlists to retrieve
        :return: List of owned playlists.

        Each item is in the following format::

            {
                'playlistId': 'PLQwVIlKxHM6rz0fDJVv_0UlXGEWf-bFys',
                'title': 'Playlist title',
                'thumbnails: [...],
                'count': 5
            }
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_liked_playlists'}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)

        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['gridRenderer']
        playlists = parse_content_list(results['items'][1:], parse_playlist)

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_content_list(contents, parse_playlist)
            playlists.extend(
                get_continuations(results, 'gridContinuation', limit - len(playlists),
                                  request_func, parse_func))

        return playlists

    def get_library_songs(self, limit: int = 25) -> List[Dict]:
        """
        Gets the songs in the user's library (liked videos are not included).
        To get liked songs and videos, use :py:func:`get_liked_songs`

        :param limit: Number of songs to retrieve
        :return: List of songs. Same format as :py:func:`get_playlist`
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_liked_videos'}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)
        if 'musicShelfRenderer' not in results:
            return []
        results = results['musicShelfRenderer']
        songs = parse_playlist_items(results['contents'][1:])

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_playlist_items(contents)
            songs.extend(
                get_continuations(results, 'musicShelfContinuation', limit - len(songs),
                                  request_func, parse_func))

        return songs

    def get_library_albums(self, limit: int = 25) -> List[Dict]:
        """
        Gets the albums in the user's library.

        :param limit: Number of albums to return
        :return: List of albums
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_liked_albums'}

        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)
        if 'gridRenderer' not in results:
            return []
        results = results['gridRenderer']
        albums = parse_albums(results['items'], False)

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_albums(contents, False)
            albums.extend(
                get_continuations(results, 'gridContinuation', limit - len(albums), request_func,
                                  parse_func))

        return albums

    def get_library_artists(self, limit: int = 25) -> List[Dict]:
        """
        Gets the artists of the songs in the user's library.

        :param limit: Number of artists to return
        :return: List of artists.

        Each item is in the following format::

            {
              "browseId": "UCxEqaQWosMHaTih-tgzDqug",
              "artist": "WildVibes",
              "subscribers": "2.91K",
              "thumbnails": [...]
            }
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_library_corpus_track_artists'}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response,
            lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit)

    def get_library_subscriptions(self, limit: int = 25) -> List[Dict]:
        """
        Gets the artists the user has subscribed to.

        :param limit: Number of artists to return
        :return: List of artists. Same format as :py:func:`get_library_artists`
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_library_corpus_artists'}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response,
            lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit)

    def get_liked_songs(self, limit: int = 100) -> Dict:
        """
        Gets playlist items for the 'Liked Songs' playlist

        :param limit: How many items to return. Default: 100
        :return: List of playlistItem dictionaries. See :py:func:`get_playlist`
        """
        return self.get_playlist('LM', limit)

    def get_history(self) -> List[Dict]:
        """
        Gets your play history in reverse chronological order

        :return: List of playlistItems, see :py:func:`get_playlist`
          The additional property ``played`` indicates when the playlistItem was played
          The additional property ``feedbackToken`` can be used to remove items with :py:func:`remove_history_items`
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_history'}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        songs = []
        for content in results:
            data = content['musicShelfRenderer']['contents']
            menu_entries = [[-1] + MENU_SERVICE + ['feedbackEndpoint', 'feedbackToken']]
            songlist = parse_playlist_items(data, menu_entries)
            for song in songlist:
                song['played'] = nav(content['musicShelfRenderer'], TITLE_TEXT)
            songs.extend(songlist)

        return songs

    def remove_history_items(self, feedbackTokens: List[str]) -> Dict:  # pragma: no cover
        """
        Remove an item from the account's history. This method does currently not work with brand accounts

        :param feedbackTokens: Token to identify the item to remove, obtained from :py:func:`get_history`
        :return: Full response
        """
        self._check_auth()
        body = {'feedbackTokens': feedbackTokens}
        endpoint = 'feedback'
        response = self._send_request(endpoint, body)

        return response

    def rate_song(self, videoId: str, rating: str = 'INDIFFERENT') -> Dict:
        """
        Rates a song ("thumbs up"/"thumbs down" interactions on YouTube Music)

        :param videoId: Video id
        :param rating: One of 'LIKE', 'DISLIKE', 'INDIFFERENT'

          | 'INDIFFERENT' removes the previous rating and assigns no rating

        :return: Full response
        """
        self._check_auth()
        body = {'target': {'videoId': videoId}}
        endpoint = prepare_like_endpoint(rating)
        if endpoint is None:
            return

        return self._send_request(endpoint, body)

    def rate_playlist(self, playlistId: str, rating: str = 'INDIFFERENT') -> Dict:
        """
        Rates a playlist/album ("Add to library"/"Remove from library" interactions on YouTube Music)
        You can also dislike a playlist/album, which has an effect on your recommendations

        :param playlistId: Playlist id
        :param rating: One of 'LIKE', 'DISLIKE', 'INDIFFERENT'

          | 'INDIFFERENT' removes the playlist/album from the library

        :return: Full response
        """
        self._check_auth()
        body = {'target': {'playlistId': playlistId}}
        endpoint = prepare_like_endpoint(rating)
        return endpoint if not endpoint else self._send_request(endpoint, body)

    def subscribe_artists(self, channelIds: List[str]) -> Dict:
        """
        Subscribe to artists. Adds the artists to your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {'channelIds': channelIds}
        endpoint = 'subscription/subscribe'
        return self._send_request(endpoint, body)

    def unsubscribe_artists(self, channelIds: List[str]) -> Dict:
        """
        Unsubscribe from artists. Removes the artists from your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {'channelIds': channelIds}
        endpoint = 'subscription/unsubscribe'
        return self._send_request(endpoint, body)
