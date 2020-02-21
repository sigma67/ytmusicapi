import requests
import json
import pkg_resources
from ytmusicapi.helpers import parse_songs

params = '?alt=json&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
base_url = 'https://music.youtube.com/youtubei/v1/'


class YTMusic:
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """
    def __init__(self, auth=""):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide authentication credentials to manage your library.
          Should be an adjusted version of `headers_auth.json.example` in the project root.
          Default: A default header is used without authentication.

        """
        self.auth = auth
        file = auth if auth else pkg_resources.resource_filename('ytmusicapi', 'headers.json')
        with open(file) as json_file:
            self.headers = json.load(json_file)

        with open(pkg_resources.resource_filename('ytmusicapi', 'context.json')) as json_file:
            self.body = json.load(json_file)

    def __send_request(self, endpoint, additionalParams=""):
        response = requests.post(base_url + endpoint + params + additionalParams, json=self.body, headers=self.headers)
        return json.loads(response.text)

    def __check_auth(self):
        if self.auth == "":
            raise Exception("Please provide authentication before using this function")

    def search(self, query):
        """
        Search for any song within YouTube music

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :return: List of song results

          Example list::

            [
                {
                    'videoId': 'ZrOKjDZOtkA',
                    'artist': 'Oasis',
                    'title': 'Wonderwall (Remastered)',
                },
                {
                    'videoId': 'Gvfgut8nAgw',
                    'artist': 'Oasis',
                    'title': 'Wonderwall',
                }
            ]


        """
        self.body['query'] = query
        self.body['params'] = 'Eg-KAQwIARAAGAAgACgAMABqChAEEAMQCRAFEAo%3D'
        endpoint = 'search'
        songs = []
        try:
            response = self.__send_request(endpoint)
            results = response['contents']['sectionListRenderer']['contents']
            for res in results:
                if 'musicShelfRenderer' in res:
                    results = res['musicShelfRenderer']['contents']
                    break

            for result in results:
                data = result['musicResponsiveListItemRenderer']
                # videoId
                videoId = data['overlay']['musicItemThumbnailOverlayRenderer']['content']['musicPlayButtonRenderer']['playNavigationEndpoint']['watchEndpoint']['videoId']
                artist = data['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
                title = data['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
                song = {'videoId': videoId, 'artist': artist, 'title': title}
                songs.append(song)
        except Exception as e:
            print(str(e))

        return songs

    def get_playlists(self):
        """
        Retrieves the content of the 'Library' page

        :return: List of owned playlists.

        Each item is in the following format::

            {
                'playlistId': 'PLQwVIlKxHM6rz0fDJVv_0UlXGEWf-bFys',
                'title': 'Playlist title'
            }

        """
        self.__check_auth()
        self.body['browseId'] = 'FEmusic_liked_playlists'
        endpoint = 'browse'
        response = self.__send_request(endpoint)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][1]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
        playlists = []
        # skip first item ("New Playlist" button)
        for result in results[1:]:
            data = result['musicTwoRowItemRenderer']
            playlistId = data['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'][2:]
            title = data['title']['runs'][0]['text']
            playlists.append({'playlistId': playlistId, 'title': title})

        return playlists

    def get_liked_songs(self, limit=1000):
        """
        Gets playlist items for the 'Liked Songs' playlist

        :param limit: How many items to return. Default: 1000
        :return: List of playlistItem dictionaries. See :py:func:`get_playlist_items`
        """
        return self.get_playlist_items('LM', limit)

    def get_history(self):
        """
        Gets your play history in reverse chronological order

        :return: List of playlistItems, see :py:func:`get_playlist_items`
          The additional property 'played' indicates when the playlistItem was played
        """
        self.__check_auth()
        self.body['browseId'] = 'FEmusic_history'
        endpoint = 'browse'
        response = self.__send_request(endpoint)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents']
        songs = []
        for content in results:
            data = content['musicShelfRenderer']['contents']
            songlist = parse_songs(data)
            for song in songlist:
                song['played'] = content['musicShelfRenderer']['title']['runs'][0]['text']
            songs.extend(songlist)

        return songs

    def rate_song(self, videoId, rating='INDIFFERENT'):
        """
        Rates a song ("thumbs up"/"thumbs down" interactions on YouTube Music)

        :param videoId: Video id
        :param rating: One of 'LIKE', 'DISLIKE', 'INDIFFERENT'

          | 'INDIFFERENT' removes the previous rating and assigns no rating
        """
        self.__check_auth()
        self.body['target'] = {'videoId': videoId}
        if rating == 'LIKE':
            endpoint = 'like/like'
        elif rating == 'DISLIKE':
            endpoint = 'like/dislike'
        elif rating == 'INDIFFERENT':
            endpoint = 'like/removelike'
        else:
            return

        self.__send_request(endpoint)


    def get_playlist_items(self, playlistId, limit=1000):
        """
        Returns a list of playlist items

        :param playlistId: Playlist id
        :param limit: How many songs to return. Default: 1000
        :return: List of playlistItem dictionaries

        Each item is in the following format::

            {
                'videoId': 'PLQwVIlKxHM6rz0fDJVv_0UlXGEWf-bFys',
                'artist': 'Artist',
                'title': 'Song Title',
                'setVideoId': '56B44F6D10557CC6'
            }

        The setVideoId is the unique id of this playlist item and
        needed for moving/removing playlist items

        """
        self.body['browseEndpointContextSupportedConfigs'] = {"browseEndpointContextMusicConfig": {"pageType": "MUSIC_PAGE_TYPE_PLAYLIST"}}
        self.body['browseId'] = "VL" + playlistId
        endpoint = 'browse'
        response = self.__send_request(endpoint)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['musicPlaylistShelfRenderer']
        songs = []
        if 'musicDetailHeaderRenderer' in response['header']: #playlist not owned
            header = response['header']['musicDetailHeaderRenderer']
        else:
            header = response['header']['musicEditablePlaylistDetailHeaderRenderer']['header']['musicDetailHeaderRenderer']
        song_count = int(header['secondSubtitle']['runs'][0]['text'].split(' ')[0])
        songs_to_get = min(limit, song_count)
        songs.extend(parse_songs(results['contents']))
        request_count = 1

        while request_count * 100 < songs_to_get:
            ctoken = results['continuations'][0]['nextContinuationData']['continuation']
            print("requested from " + str(request_count * 100))
            additionalParams = "&ctoken=" + ctoken + "&continuation=" + ctoken

            response = self.__send_request(endpoint, additionalParams)
            results = response['continuationContents']['musicPlaylistShelfContinuation']
            songs.extend(parse_songs(results['contents']))
            request_count += 1

        return songs

    def create_playlist(self, title, description, privacy_status="PRIVATE"):
        """
        Creates a new empty playlist and returns its id.

        :param title: Playlist title
        :param description: Playlist description
        :param privacy_status: Playlists can be 'PUBLIC', 'PRIVATE', or 'UNLISTED'. Default: 'PRIVATE'
        :return: ID of the YouTube playlist
        """
        self.__check_auth()
        self.body['title'] = title
        self.body['description'] = description
        self.body['privacyStatus'] = privacy_status
        endpoint = 'playlist/create'
        response = self.__send_request(endpoint)
        return response['playlistId']

    def edit_playlist(self, playlistId, title=None, description=None, privacyStatus=None):
        """
        Edit title, description or privacyStatus of a playlist.

        :param playlistId: Playlist id
        :param title: Optional. New title for the playlist
        :param description: Optional. New description for the playlist
        :param privacyStatus: Optional. New privacy status for the playlist
        :return: Status String or full response
        """
        self.__check_auth()
        self.body['playlistId'] = playlistId
        actions = []
        if title:
            actions.append({'action': 'ACTION_SET_PLAYLIST_NAME', 'playlistName': title})

        if description:
            actions.append({'action': 'ACTION_SET_PLAYLIST_DESCRIPTION', 'playlistDescription': description})

        if privacyStatus:
            actions.append({'action': 'ACTION_SET_PLAYLIST_PRIVACY', 'playlistPrivacy': privacyStatus})

        self.body['actions'] = actions
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response

    def delete_playlist(self, playlistId):
        """
        Delete a playlist.

        :param playlistId: Playlist id
        :return: Status String or full response
        """
        self.__check_auth()
        self.body['playlistId'] = playlistId
        endpoint = 'playlist/delete'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response

    def add_playlist_item(self, playlistId, videoId):
        """
        Add a song to an existing playlist

        :param playlistId: Playlist id
        :param videoId: Video id
        :return: Status String or full response
        """
        self.__check_auth()
        self.body['playlistId'] = playlistId
        self.body['actions'] = {'action': 'ACTION_ADD_VIDEO', 'addedVideoId': videoId}
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response

    def remove_playlist_item(self, playlistId, song):
        """
        Remove a song from an existing playlist

        :param playlistId: Playlist id
        :param song: Dictionary containing song information. Must contain videoId and setVideoId
        :return: Status String or full response
        """
        self.__check_auth()
        if not song['setVideoId']:
            print("Cannot remove this song, since you don't own this playlist.")
            return

        self.body['playlistId'] = playlistId
        self.body['actions'] = { 'setVideoId': song['setVideoId'], 'removedVideoId': song['videoId'], 'action': 'ACTION_REMOVE_VIDEO'}
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response
