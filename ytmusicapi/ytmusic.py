import requests
import json
import pkg_resources
import ntpath
import os
from ytmusicapi.helpers import \
    parse_playlist_items, parse_uploaded_items, parse_search_result, html_to_txt
from ytmusicapi.setup import setup

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
            self.context = json.load(json_file)

    def __send_request(self, endpoint, body, additionalParams=""):
        body.update(self.context)
        response = requests.post(base_url + endpoint + params + additionalParams, json=body, headers=self.headers)
        return json.loads(response.text)

    def __check_auth(self):
        if self.auth == "":
            raise Exception("Please provide authentication before using this function")

    @classmethod
    def setup(self):
        """
        Requests browser headers from the user and stores a configuration
        JSON file in the correct format in the current directory
        """
        setup()

    def search(self, query, filter=None):
        """
        Search YouTube music
        Returns up to 20 results within the provided category.
        By default only songs (audio-only) are returned

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
                    'videoId': 'ZrOKjDZOtkA',
                    'artist': 'Oasis',
                    'title': 'Wonderwall (Remastered)',
                    'resultType': 'song'
                },
                {
                    'videoId': 'Gvfgut8nAgw',
                    'artist': 'Oasis',
                    'title': 'Wonderwall',
                    'resultType': 'song'
                }
            ]


        """
        body = {'query': query}
        endpoint = 'search'
        search_results = []

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

        elif filter not in ['albums', 'artists', 'playlists', 'songs', 'videos', None]:
            return search_results

        response = self.__send_request(endpoint, body)

        try:
            if 'tabbedSearchResultsRenderer' in response['contents']:
                results = response['contents']['tabbedSearchResultsRenderer']['tabs'][0]['tabRenderer']['content']
            else:
                results = response['contents']

            results = results['sectionListRenderer']['contents']

            # no results
            if len(results) == 1 and 'itemSectionRenderer' in results:
                return search_results

            for res in results:
                if 'musicShelfRenderer' in res:
                    results = res['musicShelfRenderer']['contents']

                    for result in results:
                        data = result['musicResponsiveListItemRenderer']
                        type = filter[:-1] if filter else None
                        search_result = parse_search_result(data, type)
                        search_results.append(search_result)

        except Exception as e:
            print(str(e))

        return search_results

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
        body = {'browseId': 'FEmusic_liked_playlists'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
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
        body = {'browseId': 'FEmusic_history'}
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents']
        songs = []
        for content in results:
            data = content['musicShelfRenderer']['contents']
            songlist = parse_playlist_items(data)
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
        body = {'target': {'videoId': videoId}}
        if rating == 'LIKE':
            endpoint = 'like/like'
        elif rating == 'DISLIKE':
            endpoint = 'like/dislike'
        elif rating == 'INDIFFERENT':
            endpoint = 'like/removelike'
        else:
            return

        self.__send_request(endpoint, body)


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
        body = { 'browseEndpointContextSupportedConfigs':
          {
            "browseEndpointContextMusicConfig":
              {
                "pageType": "MUSIC_PAGE_TYPE_PLAYLIST"
              }
          },
          'browseId': "VL" + playlistId
        }
        endpoint = 'browse'
        response = self.__send_request(endpoint, body)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['musicPlaylistShelfRenderer']
        songs = []
        if 'musicDetailHeaderRenderer' in response['header']: #playlist not owned
            header = response['header']['musicDetailHeaderRenderer']
        else:
            header = response['header']['musicEditablePlaylistDetailHeaderRenderer']['header']['musicDetailHeaderRenderer']
        song_count = int(header['secondSubtitle']['runs'][0]['text'].split(' ')[0])
        if song_count == 0:
            return songs

        own_playlist = 'musicEditablePlaylistDetailHeaderRenderer' in response['header']
        songs.extend(parse_playlist_items(results['contents'], own_playlist))
        songs_to_get = min(limit, song_count)
        request_count = 1

        while request_count * 100 < songs_to_get:
            ctoken = results['continuations'][0]['nextContinuationData']['continuation']
            additionalParams = "&ctoken=" + ctoken + "&continuation=" + ctoken

            response = self.__send_request(endpoint, body, additionalParams)
            results = response['continuationContents']['musicPlaylistShelfContinuation']
            songs.extend(parse_playlist_items(results['contents'], own_playlist))
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
        body = {
            'title': title,
            'description': html_to_txt(description),  # YT does not allow HTML tags
            'privacyStatus': privacy_status
        }
        endpoint = 'playlist/create'
        response = self.__send_request(endpoint, body)
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
        body = {'playlistId': playlistId}
        actions = []
        if title:
            actions.append({'action': 'ACTION_SET_PLAYLIST_NAME', 'playlistName': title})

        if description:
            actions.append({'action': 'ACTION_SET_PLAYLIST_DESCRIPTION', 'playlistDescription': description})

        if privacyStatus:
            actions.append({'action': 'ACTION_SET_PLAYLIST_PRIVACY', 'playlistPrivacy': privacyStatus})

        body['actions'] = actions
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def delete_playlist(self, playlistId):
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

    def add_playlist_items(self, playlistId, videoIds):
        """
        Add songs to an existing playlist

        :param playlistId: Playlist id
        :param videoIds: List of Video ids
        :return: Status String or full response
        """
        self.__check_auth()
        body = {'playlistId': playlistId, 'actions': []}
        for videoId in videoIds:
            body['actions'].append({
                'action': 'ACTION_ADD_VIDEO',
                'addedVideoId': videoId
            })

        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def remove_playlist_items(self, playlistId, videos):
        """
        Remove songs from an existing playlist

        :param playlistId: Playlist id
        :param videos: List of PlaylistItems, see :py:func:`get_playlist_items`.
            Must contain videoId and setVideoId
        :return: Status String or full response
        """
        self.__check_auth()
        if not videos[0]['setVideoId']:
            print("Cannot remove songs, because setVideoId is missing. Do you own this playlist?")
            return
        
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

    def get_uploaded_songs(self, limit=25):
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
              "album": "Ghost Stories"
            }

        """
        self.__check_auth()
        endpoint = 'browse'
        body = {"browseId": "FEmusic_library_privately_owned_tracks"}
        response = self.__send_request(endpoint, body)
        results = response['contents']['singleColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][1]['itemSectionRenderer']['contents'][0]['musicShelfRenderer']
        songs = []

        songs.extend(parse_uploaded_items(results['contents'][1:]))

        request_count = 1
        while request_count * 25 < limit:
            ctoken = results['continuations'][0]['nextContinuationData']['continuation']
            additionalParams = "&ctoken=" + ctoken + "&continuation=" + ctoken
            response = self.__send_request(endpoint, body, additionalParams)
            results = response['continuationContents']['musicShelfContinuation']
            songs.extend(parse_uploaded_items(results['contents']))
            request_count += 1

        return songs

    def upload_song(self, filepath):
        """
        Uploads a song to YouTube Music

        :param filepath: Path to the music file
        :return: Status String or full response
        """
        self.__check_auth()
        if not os.path.isfile(filepath):
            return

        headers = self.headers
        upload_url = "https://upload.youtube.com/upload/usermusic/http?authuser=0"
        file = open(filepath, 'rb')
        req = requests.Request('POST', upload_url,
                      files={'file': file},
                      headers=headers)
        prepped = req.prepare()
        filesize = str(int(prepped.headers['content-length']) -500)

        body = "filename=" + ntpath.basename(filepath)
        headers['content-type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        headers['X-Goog-Upload-Command'] = 'start'
        headers['X-Goog-Upload-Header-Content-Length'] = filesize
        headers['X-Goog-Upload-Protocol'] = 'resumable'
        response = requests.post(upload_url, data=body, headers=headers)
        headers['X-Goog-Upload-Command'] = 'upload, finalize'
        headers['X-Goog-Upload-Offset'] = '0'
        upload_url = response.headers['X-Goog-Upload-URL']
        file.seek(0)
        response = requests.post(upload_url, files={'file': file}, headers=headers)
        file.close()
        if response.status_code == 200:
            return 'STATUS_SUCCEEDED'
        else:
            return response.content

    def delete_uploaded_song(self, uploaded_song):
        """
        Deletes a previously uploaded song

        :param uploaded_song: The uploaded song to delete,
            e.g. retrieved from :py:func:`get_uploaded_songs`
        :return: Status String or error
        """
        self.__check_auth()
        endpoint = 'music/delete_privately_owned_entity'
        body = {"entityId": uploaded_song['entityId']}
        response = self.__send_request(endpoint, body)

        if 'error' not in response:
            return 'STATUS_SUCCEEDED'
        else:
            return response['error']
