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

    def search(self, query):
        self.body['query'] = query
        self.body['params'] = 'Eg-KAQwIARAAGAAgACgAMABqChAEEAMQCRAFEAo%3D'
        endpoint = 'search'

        response = self.__send_request(endpoint)
        results = response['contents']['sectionListRenderer']['contents'][0]['musicShelfRenderer']['contents']
        songs = []
        for result in results:
            try:
                data = result['musicResponsiveListItemRenderer']
                # videoId
                videoId = data['overlay']['musicItemThumbnailOverlayRenderer']['content']['musicPlayButtonRenderer']['playNavigationEndpoint']['watchEndpoint']['videoId']
                artist = data['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
                title = data['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
                song = {'videoId': videoId, 'artist': artist, 'title': title}
                songs.append(song)
            except Exception as e:
                print(str(e))

            print(str(len(songs)) + " search results")

        return songs

    def get_playlist_items(self, playlistId, limit=1000):
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

        while len(songs) < songs_to_get:
            print("requested from " + str(request_count * 100))
            ctoken = results['continuations'][0]['nextContinuationData']['continuation']
            additionalParams = "&ctoken=" + ctoken + "&continuation=" + ctoken

            response = self.__send_request(endpoint, additionalParams)
            results = response['continuationContents']['musicPlaylistShelfContinuation']['contents']
            songs.extend(parse_songs(results))
            request_count += 1

        print(len(songs))
        return songs

    def add_playlist(self, title, description, public=False):
        self.body['title'] = title
        self.body['description'] = description
        self.body['privacyStatus'] = 'PUBLIC' if public else 'PRIVATE'
        endpoint = 'playlist/create'
        response = self.__send_request(endpoint)
        return response['playlistId']

    def delete_playlist(self, playlistId):
        self.body['playlistId'] = playlistId
        endpoint = 'playlist/delete'
        response = self.__send_request(endpoint)
        print(response)

    def add_playlist_item(self, playlistId, videoId):
        self.body['playlistId'] = playlistId
        self.body['actions'] = {'action': 'ACTION_ADD_VIDEO', 'addedVideoId': videoId}
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        print(response)

    def remove_playlist_item(self, playlistId, song):
        if not song['removeAction']:
            print("Cannot remove this song, since you don't own this playlist.")
            return

        self.body['playlistId'] = playlistId
        self.body['actions'] = song['removeAction']
        endpoint = 'browse/edit_playlist'
        response = self.__send_request(endpoint)
        print(response)