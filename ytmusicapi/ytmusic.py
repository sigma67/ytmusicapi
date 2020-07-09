import requests
import json
import unicodedata
import gettext
import pkg_resources
import ntpath
import os
from typing import List, Dict, Union, Tuple
from ytmusicapi.helpers import *
from ytmusicapi.parsers import *
from ytmusicapi.setup import setup

params = '?alt=json&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
base_url = 'https://music.youtube.com/youtubei/v1/'


class YTMusic:
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """
    def __init__(self,
                 auth: str = None,
                 user: str = None,
                 proxies: dict = None,
                 language: str = 'en'):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide a string or path to file.
          Authentication credentials are needed to manage your library.
          Should be an adjusted version of `headers_auth.json.example` in the project root.
          See :py:func:`setup` for how to fill in the correct credentials.
          Default: A default header is used without authentication.
        :param user: Optional. Specify a user ID string to use in requests.
          This is needed if you want to send requests on behalf of a brand account.
          Otherwise the default account is used. You can retrieve the user ID
          by going to https://myaccount.google.com and selecting your brand account.
          The user ID will be in the URL: https://myaccount.google.com/b/user_id/
        :param proxies: Optional. Proxy configuration in requests_ format_.

            .. _requests: https://requests.readthedocs.io/
            .. _format: https://requests.readthedocs.io/en/master/user/advanced/#proxies

        :param language: Optional. Can be used to change the language of returned data.
            English will be used by default. Available languages can be checked in
            the ytmusicapi/locales directory.
        """
        self.auth = auth
        self.proxies = proxies

        try:
            if auth is None or os.path.isfile(auth):
                file = auth if auth else pkg_resources.resource_filename(
                    'ytmusicapi', 'headers.json')
                with open(file) as json_file:
                    self.headers = json.load(json_file)
            else:
                self.headers = json.loads(auth)
        except Exception as e:
            print(
                "Failed loading provided credentials. Make sure to provide a string or a file path. "
                "Reason: " + str(e))

        with open(pkg_resources.resource_filename('ytmusicapi', 'context.json')) as json_file:
            self.context = json.load(json_file)
            self.context['context']['client']['hl'] = language
            supported_languages = [
                f for f in pkg_resources.resource_listdir('ytmusicapi', 'locales')
            ]
            if language in supported_languages:
                self.language = language
                self.lang = gettext.translation('base',
                                                localedir=pkg_resources.resource_filename(
                                                    'ytmusicapi', 'locales'),
                                                languages=[language])
                self.parser = Parser(self.lang)
            else:
                raise Exception("Language not supported. Supported languages are ")

            if user:
                self.context['context']['user']['onBehalfOfUser'] = user

        # verify authentication credentials work
        if auth:
            self.sapisid = sapisid_from_cookie(self.headers['Cookie'])
            response = self.__send_request('guide', {})
            if 'error' in response:
                raise Exception(
                    "The provided credentials are invalid. Reason given by the server: "
                    + response['error']['status'])

    def __send_request(self, endpoint: str, body: Dict, additionalParams: str = ""):
        body.update(self.context)
        if self.auth:
            self.headers["Authorization"] = get_authorization(self.sapisid + ' '
                                                              + self.headers['x-origin'])
        response = requests.post(base_url + endpoint + params + additionalParams,
                                 json=body,
                                 headers=self.headers,
                                 proxies=self.proxies)
        return json.loads(response.text)

    def __check_auth(self):
        if self.auth == "":
            raise Exception("Please provide authentication before using this function")

    @classmethod
    def setup(cls, filepath: str = None, headers_raw: str = None):
        """
        Requests browser headers from the user via command line
        and returns a string that can be passed to YTMusic()

        :param filepath: Optional filepath to store headers to.
        :param headers_raw: Optional request headers copied from browser.
            Otherwise requested from terminal
        :return: configuration headers string
        """
        return setup(filepath, headers_raw)

    ###############
    # BROWSING
    ###############

    def search(self, query: str, filter: str = None) -> List[Dict]:
        """
        Search YouTube music
        Returns up to 20 results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values:
          'songs', 'videos', 'albums', 'artists', 'playlists'.
          Default: Default search, including all types of items.
        :return: List of results depending on filter.
          resultType specifies the type of item (important for default search).
          albums, artists and playlists additionally contain a browseId, corresponding to
          albumId, channelId and playlistId (browseId='VL'+playlistId)

          Example list::

            [
              {
                "videoId": "ZrOKjDZOtkA",
                "title": "Wonderwall (Remastered)",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "album": {
                  "name": "(What's The Story) Morning Glory? (Remastered)",
                  "id": "MPREb_9nqEki4ZDpp"
                },
                "duration": "4:19",
                "thumbnails": [...],
                "resultType": "song"
              }
            ]
        """
        body = {'query': query}
        endpoint = 'search'
        search_results = []
        filters = ['albums', 'artists', 'playlists', 'songs', 'videos']
        if filter and filter not in filters:
            raise Exception(
                "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
                + ', '.join(filters))

        if filter:
            param1 = 'Eg-KAQwIA'
            param3 = 'MABqChAEEAMQCRAFEAo%3D'

            if filter == 'videos':
                param2 = 'BABGAAgACgA'
            elif filter == 'albums':
                param2 = 'BAAGAEgACgA'
            elif filter == 'artists':
                param2 = 'BAAGAAgASgA'
            elif filter == 'playlists':
                param2 = 'BAAGAAgACgB'
            else:
                param2 = 'RAAGAAgACgA'

            body['params'] = param1 + param2 + param3

        response = self.__send_request(endpoint, body)

        try:
            # no results
            if 'contents' not in response:
                return search_results

            if 'tabbedSearchResultsRenderer' in response['contents']:
                results = response['contents']['tabbedSearchResultsRenderer']['tabs'][0][
                    'tabRenderer']['content']
            else:
                results = response['contents']

            results = nav(results, SECTION_LIST)

            # no results
            if len(results) == 1 and 'itemSectionRenderer' in results:
                return search_results

            for res in results:
                if 'musicShelfRenderer' in res:
                    results = res['musicShelfRenderer']['contents']

                    for result in results:
                        data = result['musicResponsiveListItemRenderer']
                        type = filter[:-1] if filter else None
                        search_result = self.parser.parse_search_result(data, type)
                        search_results.append(search_result)

        except Exception as e:
            print(str(e))

        return search_results

    @i18n
    def get_artist(self, channelId: str) -> Dict:
        """
        Get information about an artist and their top releases (songs,
        albums, singles and videos). The top lists contain pointers
        for getting the full list of releases. For songs/videos, pass
        the browseId to :py:func:`get_playlist`. For albums/singles,
        pass browseId and params to :py:func:`get_artist_albums`.

        :param channelId: channel id of the artist
        :return: Dictionary with requested information.

        Example::

            {
                "description": "Oasis were ...",
                "views": "1838795605",
                "name": "Oasis",
                "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q",
                "subscribers": "2.3M",
                "subscribed": false,
                "thumbnails": [...],
                "songs": {
                    "browseId": "VLPLMpM3Z0118S42R1npOhcjoakLIv1aqnS1",
                    "results": [
                        {
                            "videoId": "ZrOKjDZOtkA",
                            "title": "Wonderwall (Remastered)",
                            "thumbnails": [...],
                            "artist": "Oasis",
                            "album": "(What's The Story) Morning Glory? (Remastered)"
                        }
                    ]
                },
                "albums": {
                    "results": [
                        {
                            "title": "Familiar To Millions",
                            "thumbnails": [...],
                            "year": "2018",
                            "browseId": "MPREb_AYetWMZunqA"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "singles": {
                    "results": [
                        {
                            "title": "Stand By Me (Mustique Demo)",
                            "thumbnails": [...],
                            "year": "2016",
                            "browseId": "MPREb_7MPKLhibN5G"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "videos": {
                    "results": [
                        {
                            "title": "Wonderwall",
                            "thumbnails": [...],
                            "views": "358M",
                            "videoId": "bx1Bh8ZvH84",
                            "playlistId": "PLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                        }
                    ],
                    "browseId": "VLPLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                }
            }
        """
        body = prepare_browse_endpoint("ARTIST", channelId)
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)

        artist = {'description': None, 'views': None}
        header = response['header']['musicImmersiveHeaderRenderer']
        artist['name'] = nav(header, TITLE_TEXT)
        descriptionShelf = find_object_by_key(results,
                                              'musicDescriptionShelfRenderer',
                                              is_key=True)
        if descriptionShelf:
            artist['description'] = descriptionShelf['description']['runs'][0]['text']
            artist['views'] = None if 'subheader' not in descriptionShelf else descriptionShelf[
                'subheader']['runs'][0]['text']
        subscription_button = header['subscriptionButton']['subscribeButtonRenderer']
        artist['channelId'] = subscription_button['channelId']
        artist['subscribers'] = nav(subscription_button,
                                    ['subscriberCountText', 'runs', 0, 'text'])
        artist['subscribed'] = subscription_button['subscribed']
        artist['thumbnails'] = nav(header, THUMBNAILS)
        artist['songs'] = {'browseId': None}
        if 'musicShelfRenderer' in results[0]:  # API sometimes does not return songs
            musicShelf = nav(results, MUSIC_SHELF)
            if 'navigationEndpoint' in nav(musicShelf, TITLE):
                artist['songs']['browseId'] = nav(musicShelf, TITLE + NAVIGATION_BROWSE_ID)
            artist['songs']['results'] = parse_playlist_items(musicShelf['contents'])

        categories = ['albums', 'singles', 'videos']
        categories_local = [_('albums'), _('singles'), _('videos')]
        for i, category in enumerate(categories):
            data = [
                r['musicCarouselShelfRenderer'] for r in results
                if 'musicCarouselShelfRenderer' in r
                and nav(r['musicCarouselShelfRenderer'],
                        CAROUSEL_TITLE)['text'].lower() == categories_local[i]
            ]
            if len(data) > 0:
                artist[category] = {'browseId': None, 'results': []}
                if 'navigationEndpoint' in nav(data[0], CAROUSEL_TITLE):
                    artist[category]['browseId'] = nav(data[0],
                                                       CAROUSEL_TITLE + NAVIGATION_BROWSE_ID)
                    if category in ['albums', 'singles']:
                        artist[category]['params'] = nav(
                            data[0],
                            CAROUSEL_TITLE)['navigationEndpoint']['browseEndpoint']['params']

                for item in data[0]['contents']:
                    item = item['musicTwoRowItemRenderer']
                    result = {'title': nav(item, TITLE_TEXT)}
                    result['thumbnails'] = nav(item, THUMBNAIL_RENDERER)
                    if category == 'albums':
                        result['year'] = nav(item, SUBTITLE2)
                        result['browseId'] = nav(item, TITLE + NAVIGATION_BROWSE_ID)
                    elif category == 'singles':
                        result['year'] = nav(item, SUBTITLE)
                        result['browseId'] = nav(item, TITLE + NAVIGATION_BROWSE_ID)
                    elif category == 'videos':
                        result['views'] = nav(item, SUBTITLE2).split(' ')[0]
                        result['videoId'] = nav(item, NAVIGATION_VIDEO_ID)
                        result['playlistId'] = nav(item, NAVIGATION_PLAYLIST_ID)
                    artist[category]['results'].append(result)

        return artist

    def get_artist_albums(self, channelId: str, params: str) -> List[Dict]:
        """
        Get the full list of an artist's albums or singles

        :param channelId: channel Id of the artist
        :param params: params obtained by :py:func:`get_artist`
        :return: List of albums or singles

        Example::

            {
                "browseId": "MPREb_0rtvKhqeCY0",
                "artist": "Armin van Buuren",
                "title": "This I Vow (feat. Mila Josef)",
                "thumbnails": [...],
                "type": "EP",
                "year": "2020"
            }
        """
        body = {"browseId": channelId, "params": params}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        artist = nav(response['header']['musicHeaderRenderer'], TITLE_TEXT)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST + MUSIC_SHELF)
        albums = []
        release_type = nav(results, TITLE_TEXT).lower()
        for result in results['contents']:
            data = result['musicResponsiveListItemRenderer']
            browseId = nav(data, NAVIGATION_BROWSE_ID)
            title = get_item_text(data, 0)
            thumbnails = nav(data, THUMBNAILS)
            album_type = get_item_text(data, 1) if release_type == "albums" else "Single"
            year = get_item_text(data, 1, 2) if release_type == "albums" else get_item_text(
                data, 1)
            albums.append({
                "browseId": browseId,
                "artist": artist,
                "title": title,
                "thumbnails": thumbnails,
                "type": album_type,
                "year": year
            })

        return albums

    def get_album(self, browseId: str) -> Dict:
        """
        Get information and tracks of an album

        :param browseId: browseId of the album, for example
            returned by :py:func:`search`
        :return: Dictionary with title, description, artist and tracks.

        Each track is in the following format::

            {
              "title": "Seven",
              "trackCount": "7",
              "durationMs": "1439579",
              "playlistId": "OLAK5uy_kGnhwT08mQMGw8fArBowdtlew3DpgUt9c",
              "releaseDate": {
                "year": 2016,
                "month": 10,
                "day": 28
              },
              "description": "Seven is ...",
              "thumbnails": [...],
              "artist": [
                {
                  "name": "Martin Garrix",
                  "id": "UCqJnSdHjKtfsrHi9aI-9d3g"
                }
              ],
              "tracks": [
                {
                  "index": "1",
                  "title": "WIEE (feat. Mesto)",
                  "artists": "Martin Garrix",
                  "videoId": "8xMNeXI9wxI",
                  "lengthMs": "203406",
                  "likeStatus": "INDIFFERENT"
                }
              ]
            }
        """
        body = prepare_browse_endpoint("ALBUM", browseId)
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        data = nav(response, FRAMEWORK_MUTATIONS)
        album = {}
        album_data = find_object_by_key(data, 'musicAlbumRelease', 'payload', True)
        album['title'] = album_data['title']
        album['trackCount'] = album_data['trackCount']
        album['durationMs'] = album_data['durationMs']
        album['playlistId'] = album_data['audioPlaylistId']
        album['releaseDate'] = album_data['releaseDate']
        album['description'] = find_object_by_key(data, 'musicAlbumReleaseDetail', 'payload',
                                                  True)['description']
        album['thumbnails'] = album_data['thumbnailDetails']['thumbnails']
        album['artist'] = []
        artists_data = find_objects_by_key(data, 'musicArtist', 'payload')
        for artist in artists_data:
            album['artist'].append({
                'name': artist['musicArtist']['name'],
                'id': artist['musicArtist']['externalChannelId']
            })
        album['tracks'] = []

        likes = {}
        for item in data:
            if 'musicTrackUserDetail' in item['payload']:
                like_state = item['payload']['musicTrackUserDetail']['likeState'].split('_')[-1]
                parent_track = item['payload']['musicTrackUserDetail']['parentTrack']
                if like_state in ['NEUTRAL', 'UNKNOWN']:
                    likes[parent_track] = 'INDIFFERENT'
                else:
                    likes[parent_track] = like_state[:-1]

        for item in data[4:]:
            if 'musicTrack' in item['payload']:
                track = {}
                track['index'] = item['payload']['musicTrack']['albumTrackIndex']
                track['title'] = item['payload']['musicTrack']['title']
                track['thumbnails'] = item['payload']['musicTrack']['thumbnailDetails'][
                    'thumbnails']
                track['artists'] = item['payload']['musicTrack']['artistNames']
                # in case the song is unavailable, there is no videoId
                track['videoId'] = item['payload']['musicTrack']['videoId'] if 'videoId' in item[
                    'payload']['musicTrack'] else None
                track['lengthMs'] = item['payload']['musicTrack']['lengthMs']
                track['likeStatus'] = likes[item['entityKey']]
                album['tracks'].append(track)

        return album

    ###############
    # LIBRARY
    ###############

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
        self.__check_auth()
        body = {'browseId': 'FEmusic_liked_playlists'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)

        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['gridRenderer']
        playlists = parse_playlists(results['items'][1:])

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_playlists(contents)
            playlists.extend(
                get_continuations(results, 'gridContinuation', 25, limit, request_func,
                                  parse_func))

        return playlists

    def get_library_songs(self, limit: int = 25) -> List[Dict]:
        """
        Gets the songs in the user's library (liked videos are not included).
        To get liked songs and videos, use :py:func:`get_liked_songs`

        :param limit: Number of songs to retrieve
        :return: List of songs. Same format as :py:func:`get_playlist`
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_liked_videos'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['musicShelfRenderer']
        songs = parse_playlist_items(results['contents'][1:])

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_playlist_items(contents)
            songs.extend(
                get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                                  parse_func))

        return songs

    def get_library_albums(self, limit: int = 25) -> List[Dict]:
        """
        Gets the albums in the user's library.

        :param limit: Number of albums to return
        :return: List of albums
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_liked_albums'}

        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)
        if 'gridRenderer' not in results:
            return []
        else:
            results = results['gridRenderer']
        albums = parse_albums(results['items'], False)

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_albums(contents, False)
            albums.extend(
                get_continuations(results, 'gridContinuation', 25, limit, request_func,
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
        self.__check_auth()
        body = {'browseId': 'FEmusic_library_corpus_track_artists'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['musicShelfRenderer']
        artists = parse_artists(results['contents'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_artists(contents)
            artists.extend(
                get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                                  parse_func))

        return artists

    def get_library_subscriptions(self, limit: int = 25) -> List[Dict]:
        """
        Gets the artists the user has subscribed to.

        :param limit: Number of artists to return
        :return: List of artists. Same format as :py:func:`get_library_artists`
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_library_corpus_artists'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['musicShelfRenderer']
        artists = parse_artists(results['contents'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_artists(contents)
            artists.extend(
                get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                                  parse_func))

        return artists

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
          The additional property 'played' indicates when the playlistItem was played
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_history'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        songs = []
        for content in results:
            data = content['musicShelfRenderer']['contents']
            songlist = parse_playlist_items(data)
            for song in songlist:
                song['played'] = nav(content['musicShelfRenderer'], TITLE_TEXT)
            songs.extend(songlist)

        return songs

    def rate_song(self, videoId: str, rating: str = 'INDIFFERENT') -> Dict:
        """
        Rates a song ("thumbs up"/"thumbs down" interactions on YouTube Music)

        :param videoId: Video id
        :param rating: One of 'LIKE', 'DISLIKE', 'INDIFFERENT'

          | 'INDIFFERENT' removes the previous rating and assigns no rating

        :return: Full response
        """
        self.__check_auth()
        body = {'target': {'videoId': videoId}}
        endpoint = prepare_like_endpoint(rating)
        if endpoint is None:
            return

        return self.__send_request(endpoint, body)

    def rate_playlist(self, playlistId: str, rating: str = 'INDIFFERENT') -> Dict:
        """
        Rates a playlist/album ("Add to library"/"Remove from library" interactions on YouTube Music)
        You can also dislike a playlist/album, which has an effect on your recommendations

        :param playlistId: Playlist id
        :param rating: One of 'LIKE', 'DISLIKE', 'INDIFFERENT'

          | 'INDIFFERENT' removes the playlist/album from the library

        :return: Full response
        """
        self.__check_auth()
        body = {'target': {'playlistId': playlistId}}
        endpoint = prepare_like_endpoint(rating)
        return endpoint if not endpoint else self.__send_request(endpoint, body)

    def subscribe_artists(self, channelIds: List[str]) -> Dict:
        """
        Subscribe to artists. Adds the artists to your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self.__check_auth()
        body = {'channelIds': channelIds}
        endpoint = 'subscription/subscribe'
        return self.__send_request(endpoint, body)

    def unsubscribe_artists(self, channelIds: List[str]) -> Dict:
        """
        Unsubscribe from artists. Removes the artists from your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self.__check_auth()
        body = {'channelIds': channelIds}
        endpoint = 'subscription/unsubscribe'
        return self.__send_request(endpoint, body)

    ###############
    # PLAYLISTS
    ###############

    def get_playlist(self, playlistId: str, limit: int = 100) -> Dict:
        """
        Returns a list of playlist items

        :param playlistId: Playlist id
        :param limit: How many songs to return. Default: 100
        :return: Dictionary with information about the playlist.
            The key ``tracks`` contains a List of playlistItem dictionaries

        Each item is in the following format::

            {
              "id": "PLQwVIlKxHM6qv-o99iX9R85og7IzF9YS_",
              "privacy": "PUBLIC",
              "title": "New EDM This Week 03/13/2020",
              "thumbnails": [...]
              "description": "Weekly r/EDM new release roundup. Created with github.com/sigma67/spotifyplaylist_to_gmusic",
              "author": "sigmatics",
              "year": "2020",
              "duration": "6+ hours",
              "trackCount": 237,
              "tracks": [
                {
                  "videoId": "bjGppZKiuFE",
                  "title": "Lost",
                  "artists": [
                    {
                      "name": "Guest Who",
                      "id": "UCkgCRdnnqWnUeIH7EIc3dBg"
                    },
                    {
                      "name": "Kate Wild",
                      "id": "UCwR2l3JfJbvB6aq0RnnJfWg"
                    }
                  ],
                  "album": {
                    "name": "Lost",
                    "id": "MPREb_PxmzvDuqOnC"
                  },
                  "duration": "2:58",
                  "likeStatus": "INDIFFERENT",
                  "thumbnails": [...]
                }
              ]
            }

        The setVideoId is the unique id of this playlist item and
        needed for moving/removing playlist items
        """
        browseId = "VL" + playlistId if not playlistId.startswith("VL") else playlistId
        body = prepare_browse_endpoint("PLAYLIST", browseId)
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)[0]['musicPlaylistShelfRenderer']
        playlist = {'id': results['playlistId']}
        own_playlist = 'musicEditablePlaylistDetailHeaderRenderer' in response['header']
        if not own_playlist:
            header = response['header']['musicDetailHeaderRenderer']
            playlist['privacy'] = 'PUBLIC'
        else:
            header = response['header']['musicEditablePlaylistDetailHeaderRenderer']
            playlist['privacy'] = header['editHeader']['musicPlaylistEditHeaderRenderer'][
                'privacy']
            header = header['header']['musicDetailHeaderRenderer']

        playlist['title'] = nav(header, TITLE_TEXT)
        playlist['thumbnails'] = nav(header, THUMBNAIL_CROPPED)
        if "description" in header:
            playlist["description"] = header["description"]["runs"][0]["text"]
        run_count = len(header['subtitle']['runs'])
        if run_count > 1:
            playlist['author'] = nav(header, SUBTITLE2)
            if run_count > 3:
                playlist['year'] = nav(header, SUBTITLE3)

        if len(header['secondSubtitle']['runs']) > 1:
            song_count = to_int(
                unicodedata.normalize("NFKD", header['secondSubtitle']['runs'][0]['text']),
                self.language)
            playlist['duration'] = header['secondSubtitle']['runs'][2]['text']
        else:
            playlist['duration'] = header['secondSubtitle']['runs'][0]['text']
            song_count = limit

        playlist['trackCount'] = song_count
        playlist['tracks'] = []

        if song_count > 0:
            playlist['tracks'].extend(parse_playlist_items(results['contents']))
            songs_to_get = min(limit, song_count)

            if 'continuations' in results:
                request_func = lambda additionalParams: self.__send_request(
                    endpoint, body, additionalParams)
                parse_func = lambda contents: parse_playlist_items(contents)
                playlist['tracks'].extend(
                    get_continuations(results, 'musicPlaylistShelfContinuation', 100, songs_to_get,
                                      request_func, parse_func))

        return playlist

    def create_playlist(self,
                        title: str,
                        description: str,
                        privacy_status: str = "PRIVATE",
                        video_ids: List = None,
                        source_playlist: str = None) -> Union[str, Dict]:
        """
        Creates a new empty playlist and returns its id.

        :param title: Playlist title
        :param description: Playlist description
        :param privacy_status: Playlists can be 'PUBLIC', 'PRIVATE', or 'UNLISTED'. Default: 'PRIVATE'
        :param video_ids: IDs of songs to create the playlist with
        :param source_playlist: Another playlist whose songs should be added to the new playlist
        :return: ID of the YouTube playlist or full response if there was an error
        """
        self.__check_auth()
        body = {
            'title': title,
            'description': html_to_txt(description),  # YT does not allow HTML tags
            'privacyStatus': privacy_status
        }
        if video_ids is not None:
            body['videoIds'] = video_ids

        if source_playlist is not None:
            body['sourcePlaylistId'] = source_playlist

        endpoint = 'playlist/create'
        response = self.__send_request(endpoint, body)
        return response['playlistId'] if 'playlistId' in response else response

    def edit_playlist(self,
                      playlistId: str,
                      title: str = None,
                      description: str = None,
                      privacyStatus: str = None,
                      moveItem: Tuple[str, str] = None,
                      addPlaylistId: str = None) -> Union[str, Dict]:
        """
        Edit title, description or privacyStatus of a playlist.
        You may also move an item within a playlist or append another playlist to this playlist.

        :param playlistId: Playlist id
        :param title: Optional. New title for the playlist
        :param description: Optional. New description for the playlist
        :param privacyStatus: Optional. New privacy status for the playlist
        :param moveItem: Optional. Move one item before another. Items are specified by setVideoId, see :py:func:`get_playlist`
        :param addPlaylistId: Optional. Id of another playlist to add to this playlist
        :return: Status String or full response
        """
        self.__check_auth()
        body = {'playlistId': playlistId}
        actions = []
        if title:
            actions.append({'action': 'ACTION_SET_PLAYLIST_NAME', 'playlistName': title})

        if description:
            actions.append({
                'action': 'ACTION_SET_PLAYLIST_DESCRIPTION',
                'playlistDescription': description
            })

        if privacyStatus:
            actions.append({
                'action': 'ACTION_SET_PLAYLIST_PRIVACY',
                'playlistPrivacy': privacyStatus
            })

        if moveItem:
            actions.append({
                'action': 'ACTION_MOVE_VIDEO_BEFORE',
                'setVideoId': moveItem[0],
                'movedSetVideoIdSuccessor': moveItem[1]
            })

        if addPlaylistId:
            actions.append({'action': 'ACTION_ADD_PLAYLIST', 'addedFullListId': addPlaylistId})

        body['actions'] = actions
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def delete_playlist(self, playlistId: str) -> Union[str, Dict]:
        """
        Delete a playlist.

        :param playlistId: Playlist id
        :return: Status String or full response
        """
        self.__check_auth()
        body = {'playlistId': playlistId}
        endpoint = 'playlist/delete'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def add_playlist_items(self, playlistId: str, videoIds: List[str]) -> Union[str, Dict]:
        """
        Add songs to an existing playlist

        :param playlistId: Playlist id
        :param videoIds: List of Video ids
        :return: Status String or full response
        """
        self.__check_auth()
        body = {'playlistId': playlistId, 'actions': []}
        for videoId in videoIds:
            body['actions'].append({'action': 'ACTION_ADD_VIDEO', 'addedVideoId': videoId})

        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def remove_playlist_items(self, playlistId: str, videos: List[Dict]) -> Union[str, Dict]:
        """
        Remove songs from an existing playlist

        :param playlistId: Playlist id
        :param videos: List of PlaylistItems, see :py:func:`get_playlist`.
            Must contain videoId and setVideoId
        :return: Status String or full response
        """
        self.__check_auth()
        if not videos[0]['setVideoId']:
            raise Exception(
                "Cannot remove songs, because setVideoId is missing. Do you own this playlist?")

        body = {'playlistId': playlistId, 'actions': []}
        for video in videos:
            body['actions'].append({
                'setVideoId': video['setVideoId'],
                'removedVideoId': video['videoId'],
                'action': 'ACTION_REMOVE_VIDEO'
            })

        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    ###############
    # UPLOADS
    ###############

    def get_library_upload_songs(self, limit: int = 25) -> List[Dict]:
        """
        Returns a list of uploaded songs

        :param limit: How many songs to return. Default: 25
        :return: List of uploaded songs.

        Each item is in the following format::

            {
              "entityId": "t_po_CICr2crg7OWpchDpjPjrBA",
              "videoId": "Uise6RPKoek",
              "artist": "Coldplay",
              "title": "A Sky Full Of Stars",
              "album": "Ghost Stories",
              "likeStatus": "LIKE",
              "thumbnails": [...]
            }
        """
        self.__check_auth()
        endpoint = 'browse'
        body = {"browseId": "FEmusic_library_privately_owned_tracks"}
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['musicShelfRenderer']
        songs = []

        songs.extend(parse_uploaded_items(results['contents'][1:]))

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            songs.extend(
                get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                                  parse_uploaded_items))

        return songs

    def get_library_upload_albums(self, limit: int = 25) -> List[Dict]:
        """
        Gets the albums of uploaded songs in the user's library.

        :param limit: Number of albums to return. Default: 25
        :return: List of albums as returned by :py:func:`get_library_albums`
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_library_privately_owned_releases'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)
        if 'gridRenderer' not in results:
            return []
        else:
            results = results['gridRenderer']
        albums = parse_albums(results['items'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_albums(contents)
            albums.extend(
                get_continuations(results, 'gridContinuation', 25, limit, request_func,
                                  parse_func))

        return albums

    def get_library_upload_artists(self, limit: int = 25) -> List[Dict]:
        """
        Gets the artists of uploaded songs in the user's library.

        :param limit: Number of artists to return. Default: 25
        :return: List of artists as returned by :py:func:`get_library_artists`
        """
        self.__check_auth()
        body = {'browseId': 'FEmusic_library_privately_owned_artists'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)['musicShelfRenderer']
        artists = parse_artists(results['contents'], True)

        if 'continuations' in results:
            request_func = lambda additionalParams: self.__send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_artists(contents, True)
            artists.extend(
                get_continuations(results, 'musicShelfContinuation', 25, limit, request_func,
                                  parse_func))

        return artists

    def get_library_upload_artist(self, browseId: str) -> List[Dict]:
        """
        Returns a list of uploaded tracks for the artist.

        :param browseId: Browse id of the upload artist, i.e. from :py:func:`get_library_upload_songs`
        :return: List of uploaded songs.

        Example List::

            [
              {
                "entityId": "t_po_CICr2crg7OWpchDKwoakAQ",
                "videoId": "Dtffhy8WJgw",
                "title": "Hold Me (Original Mix)",
                "artist": [
                  {
                    "name": "Jakko",
                    "id": "FEmusic_library_privately_owned_artist_detaila_po_CICr2crg7OWpchIFamFra28"
                  }
                ],
                "album": null,
                "likeStatus": "LIKE",
                "thumbnails": [...]
              }
            ]
        """
        self.__check_auth()
        body = prepare_browse_endpoint("ARTIST", browseId)
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST + MUSIC_SHELF)
        if len(results['contents']) > 1:
            results['contents'].pop(0)

        return parse_uploaded_items(results['contents'])

    def get_library_upload_album(self, browseId: str) -> Dict:
        """
        Get information and tracks of an album associated with uploaded tracks

        :param browseId: Browse id of the upload album, i.e. from i.e. from :py:func:`get_library_upload_songs`
        :return: Dictionary with title, description, artist and tracks.

        Example album::

            {
              "title": "Hard To Stop - Single",
              "thumbnails": [...]
              "year": "2013",
              "trackCount": 1,
              "duration": "4 minutes, 2 seconds",
              "tracks": [
                {
                  "entityId": "t_po_CICr2crg7OWpchDN6tnYBw",
                  "videoId": "VBQVcjJM7ak",
                  "title": "Hard To Stop (Vicetone x Ne-Yo x Daft Punk)",
                  "likeStatus": "LIKE"
                }
              ]
            }
        """
        self.__check_auth()
        body = prepare_browse_endpoint("ALBUM", browseId)
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        header = response['header']['musicDetailHeaderRenderer']
        album = {'title': nav(header, TITLE_TEXT)}
        album['thumbnails'] = nav(header, THUMBNAIL_CROPPED)
        if "description" in header:
            album["description"] = header["description"]["runs"][0]["text"]
        run_count = len(header['subtitle']['runs'])
        if run_count == 3:
            album['year'] = nav(header, SUBTITLE2)

        if run_count == 5:
            album['artist'] = {
                'name': nav(header, SUBTITLE2),
                'id': nav(header, ['subtitle', 'runs', 2] + NAVIGATION_BROWSE_ID)
            }
            album['year'] = nav(header, SUBTITLE3)

        if len(header['secondSubtitle']['runs']) > 1:
            album['trackCount'] = to_int(header['secondSubtitle']['runs'][0]['text'],
                                         self.language)
            album['duration'] = header['secondSubtitle']['runs'][2]['text']
        else:
            album['duration'] = header['secondSubtitle']['runs'][0]['text']

        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST + MUSIC_SHELF)
        album['tracks'] = parse_uploaded_items(results['contents'])
        return album

    def upload_song(self, filepath: str) -> Union[str, requests.Response]:
        """
        Uploads a song to YouTube Music

        :param filepath: Path to the music file (mp3, m4a, wma, flac or ogg)
        :return: Status String or full response
        """
        self.__check_auth()
        if not os.path.isfile(filepath):
            raise Exception("The provided file does not exist.")

        supported_filetypes = ["mp3", "m4a", "wma", "flac", "ogg"]
        if os.path.splitext(filepath)[1][1:] not in supported_filetypes:
            raise Exception(
                "The provided file type is not supported by YouTube Music. Supported file types are "
                + ', '.join(supported_filetypes))

        headers = self.headers
        upload_url = "https://upload.youtube.com/upload/usermusic/http?authuser=0"
        filesize = os.path.getsize(filepath)
        body = ("filename=" + ntpath.basename(filepath)).encode('utf-8')
        headers['content-type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        headers['X-Goog-Upload-Command'] = 'start'
        headers['X-Goog-Upload-Header-Content-Length'] = str(filesize)
        headers['X-Goog-Upload-Protocol'] = 'resumable'
        response = requests.post(upload_url, data=body, headers=headers, proxies=self.proxies)
        headers['X-Goog-Upload-Command'] = 'upload, finalize'
        headers['X-Goog-Upload-Offset'] = '0'
        upload_url = response.headers['X-Goog-Upload-URL']
        with open(filepath, 'rb') as file:
            response = requests.post(upload_url, data=file, headers=headers, proxies=self.proxies)

        if response.status_code == 200:
            return 'STATUS_SUCCEEDED'
        else:
            return response

    def delete_upload_entity(self, entityId: str) -> Union[str, Dict]:  # pragma: no cover
        """
        Deletes a previously uploaded song or album

        :param entityId: The entity id of the uploaded song or album,
            e.g. retrieved from :py:func:`get_library_upload_songs`
        :return: Status String or error
        """
        self.__check_auth()
        endpoint = 'music/delete_privately_owned_entity'
        if 'FEmusic_library_privately_owned_release_detail' in entityId:
            entityId = entityId.replace('FEmusic_library_privately_owned_release_detail', '')

        body = {"entityId": entityId}
        response = self.__send_request(endpoint, body)

        if 'error' not in response:
            return 'STATUS_SUCCEEDED'
        else:
            return response['error']
