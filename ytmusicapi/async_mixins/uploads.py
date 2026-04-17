import typing
from pathlib import Path

import requests

from ytmusicapi.continuations import get_continuations
from ytmusicapi.helpers import *
from ytmusicapi.navigation import *
from ytmusicapi.parsers.albums import parse_album_header
from ytmusicapi.parsers.library import (
    get_library_contents,
    parse_library_albums,
    parse_library_artists,
    pop_songs_random_mix,
)
from ytmusicapi.parsers.uploads import parse_uploaded_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType

from ..auth.types import AuthType
from ..enums import ResponseStatus
from ..exceptions import YTMusicUserError
from ._protocol import MixinProtocol
from ._utils import LibraryOrderType, prepare_order_params, validate_order_parameter


class UploadsMixin(MixinProtocol):
    def get_library_upload_songs(
        self, limit: int | None = 25, order: LibraryOrderType | None = None
    ) -> JsonList:
        """
        Returns a list of uploaded songs

        :param limit: How many songs to return. ``None`` retrieves them all. Default: 25
        :param order: Order of songs to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of uploaded songs.

        Each item is in the following format::

            {
              "entityId": "t_po_CICr2crg7OWpchDpjPjrBA",
              "videoId": "Uise6RPKoek",
              "artists": [{
                'name': 'Coldplay',
                'id': 'FEmusic_library_privately_owned_artist_detaila_po_CICr2crg7OWpchIIY29sZHBsYXk',
              }],
              "title": "A Sky Full Of Stars",
              "album": "Ghost Stories",
              "likeStatus": "LIKE",
              "thumbnails": [...]
            }
        """
        self._check_auth()
        endpoint = "browse"
        body = {"browseId": "FEmusic_library_privately_owned_tracks"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        response = self._send_request(endpoint, body)
        results = get_library_contents(response, MUSIC_SHELF)
        if results is None:
            return []
        pop_songs_random_mix(results)
        songs: JsonList = parse_uploaded_items(results["contents"])

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            remaining_limit = None if limit is None else (limit - len(songs))
            songs.extend(
                get_continuations(
                    results, "musicShelfContinuation", remaining_limit, request_func, parse_uploaded_items
                )
            )

        return songs

    def get_library_upload_albums(
        self, limit: int | None = 25, order: LibraryOrderType | None = None
    ) -> JsonList:
        """
        Gets the albums of uploaded songs in the user's library.

        :param limit: Number of albums to return. ``None`` retrives them all. Default: 25
        :param order: Order of albums to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of albums as returned by :py:func:`get_library_albums`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_privately_owned_releases"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_albums(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_upload_artists(
        self, limit: int | None = 25, order: LibraryOrderType | None = None
    ) -> JsonList:
        """
        Gets the artists of uploaded songs in the user's library.

        :param limit: Number of artists to return. ``None`` retrieves them all. Default: 25
        :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of artists as returned by :py:func:`get_library_artists`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_privately_owned_artists"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_upload_artist(self, browseId: str, limit: int = 25) -> JsonList:
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
                "artists": [
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
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        if len(results["contents"]) > 1:
            results["contents"].pop(0)

        items = parse_uploaded_items(results["contents"])

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_func: ParseFuncType = lambda contents: parse_uploaded_items(contents)
            remaining_limit = None if limit is None else (limit - len(items))
            items.extend(
                get_continuations(
                    results, "musicShelfContinuation", remaining_limit, request_func, parse_func
                )
            )

        return items

    def get_library_upload_album(self, browseId: str) -> JsonDict:
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
                  "duration_seconds": 255,
                  "artists": None,
                  "album": {
                    "name": "18 Months",
                    "id": "FEmusic_library_privately_owned_release_detailb_po_55chars"
                  },
                  "likeStatus": "INDIFFERENT",
                  "thumbnails": None
                },
        """
        self._check_auth()
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        album = parse_album_header(response)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        album["tracks"] = parse_uploaded_items(results["contents"])
        album["duration_seconds"] = sum_total_duration(album)
        return album

    def upload_song(self, filepath: str) -> ResponseStatus | requests.Response:
        """
        Uploads a song to YouTube Music

        :param filepath: Path to the music file (mp3, m4a, wma, flac or ogg)
        :return: Status String or full response
        """
        self._check_auth()
        if not self.auth_type == AuthType.BROWSER:
            raise YTMusicUserError("Please provide browser authentication before using this function")
        fp = Path(filepath)
        if not fp.is_file():
            raise YTMusicUserError("The provided file does not exist.")

        supported_filetypes = ["mp3", "m4a", "wma", "flac", "ogg"]
        if fp.suffix[1:] not in supported_filetypes:
            raise YTMusicUserError(
                "The provided file type is not supported by YouTube Music. Supported file types are "
                + ", ".join(supported_filetypes)
            )

        headers = self.headers.copy()
        upload_url = f"https://upload.youtube.com/upload/usermusic/http?authuser={headers['x-goog-authuser']}"
        filesize = fp.stat().st_size
        if filesize >= 314572800:  # 300MB in bytes
            msg = f"File {fp} has size {filesize} bytes, which is larger than the limit of 300MB"
            raise YTMusicUserError(msg)

        body = ("filename=" + fp.name).encode("utf-8")
        headers.pop("content-encoding", None)
        headers["content-type"] = "application/x-www-form-urlencoded;charset=utf-8"
        headers["X-Goog-Upload-Command"] = "start"
        headers["X-Goog-Upload-Header-Content-Length"] = str(filesize)
        headers["X-Goog-Upload-Protocol"] = "resumable"
        response = requests.post(upload_url, data=body, headers=headers, proxies=self.proxies)
        headers["X-Goog-Upload-Command"] = "upload, finalize"
        headers["X-Goog-Upload-Offset"] = "0"
        upload_url = response.headers["X-Goog-Upload-URL"]
        with open(fp, "rb") as file:
            response = requests.post(upload_url, data=file, headers=headers, proxies=self.proxies)

        if response.status_code == 200:
            return ResponseStatus.SUCCEEDED
        else:
            return response

    def delete_upload_entity(self, entityId: str) -> str | JsonDict:  # pragma: no cover
        """
        Deletes a previously uploaded song or album

        :param entityId: The entity id of the uploaded song or album,
            e.g. retrieved from :py:func:`get_library_upload_songs`
        :return: Status String or error
        """
        self._check_auth()
        endpoint = "music/delete_privately_owned_entity"
        if "FEmusic_library_privately_owned_release_detail" in entityId:
            entityId = entityId.replace("FEmusic_library_privately_owned_release_detail", "")

        body = {"entityId": entityId}
        response = self._send_request(endpoint, body)

        if "error" not in response:
            return ResponseStatus.SUCCEEDED
        else:
            return typing.cast(str, response["error"])
