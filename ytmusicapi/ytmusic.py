import requests
import json
import pkg_resources
from ytmusicapi.helpers import parse_songs

params = '?alt=json&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
base_url = 'https://music.youtube.com/youtubei/v1/'

class YTMusic:
    def __init__(self, auth=""):
        self.auth = auth
        file = auth if auth else pkg_resources.resource_filename('ytmusicapi', 'headers.json')
        with open(file) as json_file:
            self.headers = json.load(json_file)

        with open(pkg_resources.resource_filename('ytmusicapi','context.json')) as json_file:
            self.body = json.load(json_file)

    def __send_request(self, endpoint, additionalParams=""):
        response = requests.post(base_url + endpoint + params + additionalParams, json=self.body, headers=self.headers)
        return json.loads(response.text)

    def __check_auth(self):
        if self.auth == "":
            raise Exception("Please provide authentication before using this function")

    def search(self, query):
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
        :return: List of owned playlists
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
        return self.get_playlist_items('LM', limit)

    def get_history(self):
        self.__check_auth()
        self.body['browseId'] = 'FEmusic_history'
        endpoint = 'browse'
        response = self.__send_request(endpoint)
        raise NotImplementedError

    def get_playlist_items(self, playlistId, limit=1000):
        """
        Returns a list of playlist items
        :param playlistId: The playlist's id
        :param limit: How many songs to return. Default: 1000
        :return: List of playlistItem dictionaries, containing { videoId, artist, title, setVideoId }
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

        :param playlistId: Playlist ID
        :param title: Optional. New title for the playlist
        :param description: Optional. New description for the playlist
        :param privacyStatus: Optional. New privacy status for the playlist
        :return: Request status
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
        self.__check_auth()
        self.body['playlistId'] = playlistId
        endpoint = 'playlist/delete'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response

    def add_playlist_item(self, playlistId, videoId):
        self.__check_auth()
        self.body['playlistId'] = playlistId
        self.body['actions'] = {'action': 'ACTION_ADD_VIDEO', 'addedVideoId': videoId}
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response

    def remove_playlist_item(self, playlistId, song):
        self.__check_auth()
        if not song['setVideoId']:
            print("Cannot remove this song, since you don't own this playlist.")
            return

        self.body['playlistId'] = playlistId
        self.body['actions'] = { 'setVideoId': song['setVideoId'], 'removedVideoId': song['videoId'], 'action': 'ACTION_REMOVE_VIDEO'}
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        return response['status'] if 'status' in response else response