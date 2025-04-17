from collections.abc import Callable
from random import randint

from requests import Response

from ytmusicapi.continuations import *
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.library import *
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncDictType, ParseFuncType, RequestFuncType

from ..exceptions import YTMusicServerError
from ._protocol import MixinProtocol
from ._utils import *


class LibraryMixin(MixinProtocol):
    def get_library_playlists(self, limit: int | None = 25) -> JsonList:
        """
        Retrieves the playlists in the user's library.

        :param limit: Number of playlists to retrieve. ``None`` retrieves them all.
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
        body = {"browseId": "FEmusic_liked_playlists"}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        results = get_library_contents(response, GRID)
        if results is None:
            return []
        playlists = parse_content_list(results["items"][1:], parse_playlist)

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_playlist)
            remaining_limit = None if limit is None else (limit - len(playlists))
            playlists.extend(
                get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_func)
            )

        return playlists

    def get_library_songs(
        self, limit: int = 25, validate_responses: bool = False, order: LibraryOrderType | None = None
    ) -> JsonList:
        """
        Gets the songs in the user's library (liked videos are not included).
        To get liked songs and videos, use :py:func:`get_liked_songs`

        :param limit: Number of songs to retrieve
        :param validate_responses: Flag indicating if responses from YTM should be validated and retried in case
            when some songs are missing. Default: False
        :param order: Order of songs to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of songs. Same format as :py:func:`get_playlist`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_liked_videos"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        per_page = 25

        request_func: RequestFuncType = lambda additionalParams: self._send_request(endpoint, body)
        parse_func: ParseFuncDictType = lambda raw_response: parse_library_songs(raw_response)

        if validate_responses and limit is None:
            raise YTMusicUserError("Validation is not supported without a limit parameter.")

        if validate_responses:
            validate_func: Callable[[JsonDict], bool] = lambda parsed: validate_response(
                parsed, per_page, limit, 0
            )
            response = resend_request_until_parsed_response_is_valid(
                request_func, "", parse_func, validate_func, 3
            )
        else:
            response = parse_func(request_func(""))

        results = response["results"]
        songs: JsonList | None = response["parsed"]
        if songs is None:
            return []

        if "continuations" in results:
            request_continuations_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_continuations_func = lambda contents: parse_playlist_items(contents)

            if validate_responses:
                songs.extend(
                    get_validated_continuations(
                        results,
                        "musicShelfContinuation",
                        limit - len(songs),
                        per_page,
                        request_continuations_func,
                        parse_continuations_func,
                    )
                )
            else:
                remaining_limit = None if limit is None else (limit - len(songs))
                songs.extend(
                    get_continuations(
                        results,
                        "musicShelfContinuation",
                        remaining_limit,
                        request_continuations_func,
                        parse_continuations_func,
                    )
                )

        return songs

    def get_library_albums(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the albums in the user's library.

        :param limit: Number of albums to return
        :param order: Order of albums to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of albums.

        Each item is in the following format::

            {
              "browseId": "MPREb_G8AiyN7RvFg",
              "playlistId": "OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc",
              "title": "Beautiful",
              "type": "Album",
              "thumbnails": [...],
              "artists": [{
                "name": "Project 46",
                "id": "UCXFv36m62USAN5rnVct9B4g"
              }],
              "year": "2015"
            }
        """
        self._check_auth()
        body = {"browseId": "FEmusic_liked_albums"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)

        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_albums(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_artists(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the artists of the songs in the user's library.

        :param limit: Number of artists to return
        :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
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
        body = {"browseId": "FEmusic_library_corpus_track_artists"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_subscriptions(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Gets the artists the user has subscribed to.

        :param limit: Number of artists to return
        :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of artists. Same format as :py:func:`get_library_artists`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_corpus_artists"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_podcasts(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Get podcasts the user has added to the library

        :param limit: Number of podcasts to return
        :param order: Order of podcasts to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of podcasts. New Episodes playlist is the first podcast returned, but only if subscribed to relevant podcasts.

        Example::

            [
                {
                    "title": "New Episodes",
                    "channel":
                    {
                        "id": null,
                        "name": "Auto playlist"
                    },
                    "browseId": "VLRDPN",
                    "podcastId": "RDPN",
                    "thumbnails": [...]
                },
                {
                    "title": "5 Minuten Harry Podcast",
                    "channel":
                    {
                        "id": "UCDIDXF4WM1qQzerrxeEfSdA",
                        "name": "coldmirror"
                    },
                    "browseId": "MPSPPLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH",
                    "podcastId": "PLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH",
                    "thumbnails": [...]
                }
            ]
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_non_music_audio_list"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_podcasts(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_library_channels(self, limit: int = 25, order: LibraryOrderType | None = None) -> JsonList:
        """
        Get channels the user has added to the library

        :param limit: Number of channels to return
        :param order: Order of channels to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order.
        :return: List of channels.

        Example::

            [
                {
                    "browseId": "UCRFF8xw5dg9mL4r5ryFOtKw",
                    "artist": "Jumpers Jump",
                    "subscribers": "1.54M",
                    "thumbnails": [...]
                },
                {
                    "browseId": "UCQ3f2_sO3NJyDkuCxCNSOVA",
                    "artist": "BROWN BAG",
                    "subscribers": "74.2K",
                    "thumbnails": [...]
                }
            ]
        """
        self._check_auth()
        body = {"browseId": "FEmusic_library_non_music_audio_channels_list"}
        validate_order_parameter(order)
        if order is not None:
            body["params"] = prepare_order_params(order)
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        return parse_library_artists(
            response, lambda additionalParams: self._send_request(endpoint, body, additionalParams), limit
        )

    def get_history(self) -> JsonList:
        """
        Gets your play history in reverse chronological order

        :return: List of playlistItems, see :py:func:`get_playlist`
          The additional property ``played`` indicates when the playlistItem was played
          The additional property ``feedbackToken`` can be used to remove items with :py:func:`remove_history_items`
        """
        self._check_auth()
        body = {"browseId": "FEmusic_history"}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        songs = []
        for content in results:
            data = nav(content, [*MUSIC_SHELF, "contents"], True)
            if not data:
                error = nav(content, ["musicNotifierShelfRenderer", *TITLE], True)
                raise YTMusicServerError(error)
            menu_entries = [[*MENU_SERVICE, *FEEDBACK_TOKEN]]
            songlist = parse_playlist_items(data, menu_entries)
            for song in songlist:
                song["played"] = nav(content["musicShelfRenderer"], TITLE_TEXT)
            songs.extend(songlist)

        return songs

    def add_history_item(self, song: JsonDict) -> Response:
        """
        Add an item to the account's history using the playbackTracking URI
        obtained from :py:func:`get_song`. A ``204`` return code indicates success.

        Usage::

            song = yt_auth.get_song(videoId)
            response = yt_auth.add_history_item(song)

        .. note::

            You need to use the same YTMusic instance as you used for :py:func:`get_song`.

        :param song: Dictionary as returned by :py:func:`get_song`
        :return: Full response. response.status_code is 204 if successful
        """
        self._check_auth()
        url = song["playbackTracking"]["videostatsPlaybackUrl"]["baseUrl"]
        CPNA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        cpn = "".join(CPNA[randint(0, 256) & 63] for _ in range(0, 16))
        params = {"ver": 2, "c": "WEB_REMIX", "cpn": cpn}
        return self._send_get_request(url, params)

    def remove_history_items(self, feedbackTokens: list[str]) -> JsonDict:  # pragma: no cover
        """
        Remove an item from the account's history. This method does currently not work with brand accounts

        :param feedbackTokens: Token to identify the item to remove, obtained from :py:func:`get_history`
        :return: Full response
        """
        self._check_auth()
        body = {"feedbackTokens": feedbackTokens}
        endpoint = "feedback"
        response = self._send_request(endpoint, body)

        return response

    def rate_song(self, videoId: str, rating: LikeStatus = LikeStatus.INDIFFERENT) -> JsonDict | None:
        """
        Rates a song ("thumbs up"/"thumbs down" interactions on YouTube Music)

        :param videoId: Video id
        :param rating: One of ``LIKE``, ``DISLIKE``, ``INDIFFERENT``

          | ``INDIFFERENT`` removes the previous rating and assigns no rating

        :return: Full response
        :raises: YTMusicUserError if an invalid rating ir povided
        """
        self._check_auth()
        body = {"target": {"videoId": videoId}}
        endpoint = prepare_like_endpoint(rating)
        return self._send_request(endpoint, body)

    def edit_song_library_status(self, feedbackTokens: list[str] | None = None) -> JsonDict:
        """
        Adds or removes a song from your library depending on the token provided.

        :param feedbackTokens: List of feedbackTokens obtained from authenticated requests
            to endpoints that return songs (i.e. :py:func:`get_album`)
        :return: Full response
        """
        self._check_auth()
        body = {"feedbackTokens": feedbackTokens}
        endpoint = "feedback"
        return self._send_request(endpoint, body)

    def rate_playlist(self, playlistId: str, rating: LikeStatus = LikeStatus.INDIFFERENT) -> JsonDict:
        """
        Rates a playlist/album ("Add to library"/"Remove from library" interactions on YouTube Music)
        You can also dislike a playlist/album, which has an effect on your recommendations

        :param playlistId: Playlist id
        :param rating: One of ``LIKE``, ``DISLIKE``, ``INDIFFERENT``

          | ``INDIFFERENT`` removes the playlist/album from the library

        :return: Full response
        :raises: YTMusicUserError if an invalid rating is provided
        """
        self._check_auth()
        body = {"target": {"playlistId": playlistId}}
        endpoint = prepare_like_endpoint(rating)
        return self._send_request(endpoint, body)

    def subscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """
        Subscribe to artists. Adds the artists to your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {"channelIds": channelIds}
        endpoint = "subscription/subscribe"
        return self._send_request(endpoint, body)

    def unsubscribe_artists(self, channelIds: list[str]) -> JsonDict:
        """
        Unsubscribe from artists. Removes the artists from your library

        :param channelIds: Artist channel ids
        :return: Full response
        """
        self._check_auth()
        body = {"channelIds": channelIds}
        endpoint = "subscription/unsubscribe"
        return self._send_request(endpoint, body)

    def get_account_info(self) -> JsonDict:
        """
        Gets information about the currently authenticated user's account.

        :return: Dictionary with user's account name, channel handle, and URL of their account photo.

        Example::

            {
                "accountName": "Sample User",
                "channelHandle": "@SampleUser
                "accountPhotoUrl": "https://yt3.ggpht.com/sample-user-photo"
            }
        """
        self._check_auth()
        endpoint = "account/account_menu"
        response = self._send_request(endpoint, {})

        ACCOUNT_INFO = [
            "actions",
            0,
            "openPopupAction",
            "popup",
            "multiPageMenuRenderer",
            "header",
            "activeAccountHeaderRenderer",
        ]
        ACCOUNT_RUNS_TEXT = ["runs", 0, "text"]
        ACCOUNT_NAME = [*ACCOUNT_INFO, "accountName", *ACCOUNT_RUNS_TEXT]
        ACCOUNT_CHANNEL_HANDLE = [*ACCOUNT_INFO, "channelHandle", *ACCOUNT_RUNS_TEXT]
        ACCOUNT_PHOTO_URL = [*ACCOUNT_INFO, "accountPhoto", "thumbnails", 0, "url"]

        account_name = nav(response, ACCOUNT_NAME)
        channel_handle = nav(response, ACCOUNT_CHANNEL_HANDLE, none_if_absent=True)
        account_photo_url = nav(response, ACCOUNT_PHOTO_URL)

        return {
            "accountName": account_name,
            "channelHandle": channel_handle,
            "accountPhotoUrl": account_photo_url,
        }
