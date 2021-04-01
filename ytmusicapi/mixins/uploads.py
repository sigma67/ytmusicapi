import requests
import ntpath
import os
from typing import List, Dict, Union
from ytmusicapi.helpers import *
from ytmusicapi.parsers.library import *
from ytmusicapi.parsers.albums import *
from ytmusicapi.parsers.uploads import *


class UploadsMixin:
    def get_library_upload_songs(self, limit: int = 25, order: str = None) -> List[Dict]:
        """
        Returns a list of uploaded songs

        :param limit: How many songs to return. Default: 25
        :param order: Order of songs to return. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'. Default: Default order.
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
        self._check_auth()
        endpoint = 'browse'
        body = {"browseId": "FEmusic_library_privately_owned_tracks"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        response = self._send_request(endpoint, body)
        results = find_object_by_key(nav(response, SINGLE_COLUMN_TAB + SECTION_LIST),
                                     'itemSectionRenderer')
        results = nav(results, ITEM_SECTION)
        if 'musicShelfRenderer' not in results:
            return []
        else:
            results = results['musicShelfRenderer']

        songs = []

        songs.extend(parse_uploaded_items(results['contents'][1:]))

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            songs.extend(
                get_continuations(results, 'musicShelfContinuation', limit - len(songs),
                                  request_func, parse_uploaded_items))

        return songs

    def get_library_upload_albums(self, limit: int = 25, order: str = None) -> List[Dict]:
        """
        Gets the albums of uploaded songs in the user's library.

        :param limit: Number of albums to return. Default: 25
        :param order: Order of albums to return. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'. Default: Default order.
        :return: List of albums as returned by :py:func:`get_library_albums`
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_library_privately_owned_releases'}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        return parse_library_albums(
            response,
            lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit)

    def get_library_upload_artists(self, limit: int = 25, order: str = None) -> List[Dict]:
        """
        Gets the artists of uploaded songs in the user's library.

        :param limit: Number of artists to return. Default: 25
        :param order: Order of artists to return. Allowed values: 'a_to_z', 'z_to_a', 'recently_added'. Default: Default order.
        :return: List of artists as returned by :py:func:`get_library_artists`
        """
        self._check_auth()
        body = {'browseId': 'FEmusic_library_privately_owned_artists'}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response,
            lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit)

    def get_library_upload_artist(self, browseId: str, limit: int = 25) -> List[Dict]:
        """
        Returns a list of uploaded tracks for the artist.

        :param browseId: Browse id of the upload artist, i.e. from :py:func:`get_library_upload_songs`
        :param limit: Number of songs to return (increments of 25).
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
        self._check_auth()
        body = prepare_browse_endpoint("ARTIST", browseId)
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        if len(results['contents']) > 1:
            results['contents'].pop(0)

        items = parse_uploaded_items(results['contents'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_uploaded_items(contents)
            items.extend(
                get_continuations(results, 'musicShelfContinuation', limit, request_func,
                                  parse_func))

        return items

    def get_library_upload_album(self, browseId: str) -> Dict:
        """
        Get information and tracks of an album associated with uploaded tracks

        :param browseId: Browse id of the upload album, i.e. from i.e. from :py:func:`get_library_upload_songs`
        :return: Dictionary with title, description, artist and tracks.

        Example album::

            {
              "title": "18 Months",
              "type": "Album",
              "thumbnails": [...],
              "trackCount": 7,
              "duration": "24 minutes",
              "audioPlaylistId": "MLPRb_po_55chars",
              "tracks": [
                {
                  "entityId": "t_po_22chars",
                  "videoId": "FVo-UZoPygI",
                  "title": "Feel So Close",
                  "duration": "4:15",
                  "artist": None,
                  "album": {
                    "name": "18 Months",
                    "id": "FEmusic_library_privately_owned_release_detailb_po_55chars"
                  },
                  "likeStatus": "INDIFFERENT",
                  "thumbnails": None
                },
        """
        self._check_auth()
        body = prepare_browse_endpoint("ALBUM", browseId)
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        album = parse_album_header(response)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        album['tracks'] = parse_uploaded_items(results['contents'])
        return album

    def upload_song(self, filepath: str) -> Union[str, requests.Response]:
        """
        Uploads a song to YouTube Music

        :param filepath: Path to the music file (mp3, m4a, wma, flac or ogg)
        :return: Status String or full response
        """
        self._check_auth()
        if not os.path.isfile(filepath):
            raise Exception("The provided file does not exist.")

        supported_filetypes = ["mp3", "m4a", "wma", "flac", "ogg"]
        if os.path.splitext(filepath)[1][1:] not in supported_filetypes:
            raise Exception(
                "The provided file type is not supported by YouTube Music. Supported file types are "
                + ', '.join(supported_filetypes))

        headers = self.headers.copy()
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
        self._check_auth()
        endpoint = 'music/delete_privately_owned_entity'
        if 'FEmusic_library_privately_owned_release_detail' in entityId:
            entityId = entityId.replace('FEmusic_library_privately_owned_release_detail', '')

        body = {"entityId": entityId}
        response = self._send_request(endpoint, body)

        if 'error' not in response:
            return 'STATUS_SUCCEEDED'
        else:
            return response['error']
