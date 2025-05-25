from ytmusicapi.continuations import *
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.helpers import sum_total_duration
from ytmusicapi.navigation import *
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist
from ytmusicapi.parsers.playlists import *
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncBodyType, RequestFuncType

from ._protocol import MixinProtocol
from ._utils import *


class PlaylistsMixin(MixinProtocol):
    def get_playlist(
        self, playlistId: str, limit: int | None = 100, related: bool = False, suggestions_limit: int = 0
    ) -> JsonDict:
        """
        Returns a list of playlist items

        :param playlistId: Playlist id
        :param limit: How many songs to return. ``None`` retrieves them all. Default: 100
        :param related: Whether to fetch 10 related playlists or not. Default: False
        :param suggestions_limit: How many suggestions to return. The result is a list of
            suggested playlist items (videos) contained in a "suggestions" key.
            7 items are retrieved in each internal request. Default: 0
        :return: Dictionary with information about the playlist.
            The key ``tracks`` contains a List of playlistItem dictionaries

        The result is in the following format::

            {
              "id": "PLQwVIlKxHM6qv-o99iX9R85og7IzF9YS_",
              "privacy": "PUBLIC",
              "title": "New EDM This Week 03/13/2020",
              "thumbnails": [...]
              "description": "Weekly r/EDM new release roundup. Created with github.com/sigma67/spotifyplaylist_to_gmusic",
              "author": "sigmatics",
              "year": "2020",
              "duration": "6+ hours",
              "duration_seconds": 52651,
              "trackCount": 237,
              "suggestions": [
                  {
                    "videoId": "HLCsfOykA94",
                    "title": "Mambo (GATTÜSO Remix)",
                    "artists": [{
                        "name": "Nikki Vianna",
                        "id": "UCMW5eSIO1moVlIBLQzq4PnQ"
                      }],
                    "album": {
                      "name": "Mambo (GATTÜSO Remix)",
                      "id": "MPREb_jLeQJsd7U9w"
                    },
                    "likeStatus": "LIKE",
                    "thumbnails": [...],
                    "isAvailable": true,
                    "isExplicit": false,
                    "duration": "3:32",
                    "duration_seconds": 212,
                    "setVideoId": "to_be_updated_by_client"
                  }
              ],
              "related": [
                  {
                    "title": "Presenting MYRNE",
                    "playlistId": "RDCLAK5uy_mbdO3_xdD4NtU1rWI0OmvRSRZ8NH4uJCM",
                    "thumbnails": [...],
                    "description": "Playlist • YouTube Music"
                  }
              ],
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
                  "duration_seconds": 178,
                  "setVideoId": "748EE8..."
                  "likeStatus": "INDIFFERENT",
                  "thumbnails": [...],
                  "isAvailable": True,
                  "isExplicit": False,
                  "videoType": "MUSIC_VIDEO_TYPE_OMV",
                  "feedbackTokens": {
                    "add": "AB9zfpJxtvrU...",
                    "remove": "AB9zfpKTyZ..."
                }
              ]
            }

        The setVideoId is the unique id of this playlist item and
        needed for moving/removing playlist items
        """
        browseId = "VL" + playlistId if not playlistId.startswith("VL") else playlistId
        body = {"browseId": browseId}
        endpoint = "browse"
        request_func: RequestFuncType = lambda additionalParams: self._send_request(
            endpoint, body, additionalParams
        )
        response = request_func("")

        request_func_continuations: RequestFuncBodyType = lambda body: self._send_request(endpoint, body)
        if playlistId.startswith("OLA") or playlistId.startswith("VLOLA"):
            return parse_audio_playlist(response, limit, request_func_continuations)

        header_data = nav(response, [*TWO_COLUMN_RENDERER, *TAB_CONTENT, *SECTION_LIST_ITEM])
        section_list = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION])
        playlist: JsonDict = {}
        playlist["owned"] = EDITABLE_PLAYLIST_DETAIL_HEADER[0] in header_data
        if not playlist["owned"]:
            header = nav(header_data, RESPONSIVE_HEADER)
            playlist["id"] = nav(
                header,
                ["buttons", 1, "musicPlayButtonRenderer", "playNavigationEndpoint", *WATCH_PLAYLIST_ID],
                True,
            )
            playlist["privacy"] = "PUBLIC"
        else:
            playlist["id"] = nav(header_data, [*EDITABLE_PLAYLIST_DETAIL_HEADER, *PLAYLIST_ID])
            header = nav(header_data, [*EDITABLE_PLAYLIST_DETAIL_HEADER, *HEADER, *RESPONSIVE_HEADER])
            playlist["privacy"] = header_data[EDITABLE_PLAYLIST_DETAIL_HEADER[0]]["editHeader"][
                "musicPlaylistEditHeaderRenderer"
            ]["privacy"]

        description_shelf = nav(header, ["description", *DESCRIPTION_SHELF], True)
        playlist["description"] = (
            "".join([run["text"] for run in description_shelf["description"]["runs"]])
            if description_shelf
            else None
        )

        playlist.update(parse_playlist_header_meta(header))

        playlist.update(parse_song_runs(nav(header, SUBTITLE_RUNS)[2 + playlist["owned"] * 2 :]))

        # suggestions and related are missing e.g. on liked songs
        playlist["related"] = []
        if "continuations" in section_list:
            additionalParams = get_continuation_params(section_list)
            if playlist["owned"] and (suggestions_limit > 0 or related):
                parse_func: ParseFuncType = lambda results: parse_playlist_items(results)
                suggested = request_func(additionalParams)
                continuation = nav(suggested, SECTION_LIST_CONTINUATION)
                additionalParams = get_continuation_params(continuation)
                suggestions_shelf = nav(continuation, CONTENT + MUSIC_SHELF)
                playlist["suggestions"] = get_continuation_contents(suggestions_shelf, parse_func)

                parse_func = lambda results: parse_playlist_items(results)
                playlist["suggestions"].extend(
                    get_reloadable_continuations(
                        suggestions_shelf,
                        "musicShelfContinuation",
                        suggestions_limit - len(playlist["suggestions"]),
                        request_func,
                        parse_func,
                    )
                )

            if related:
                response = request_func(additionalParams)
                continuation = nav(response, SECTION_LIST_CONTINUATION, True)
                if continuation:
                    parse_func = lambda results: parse_content_list(results, parse_playlist)
                    playlist["related"] = get_continuation_contents(
                        nav(continuation, CONTENT + CAROUSEL), parse_func
                    )

        playlist["tracks"] = []
        content_data = nav(section_list, [*CONTENT, "musicPlaylistShelfRenderer"])
        if "contents" in content_data:
            playlist["tracks"] = parse_playlist_items(content_data["contents"])

            parse_func = lambda contents: parse_playlist_items(contents)
            playlist["tracks"].extend(
                get_continuations_2025(content_data, limit, request_func_continuations, parse_func)
            )

        playlist["duration_seconds"] = sum_total_duration(playlist)
        return playlist

    def get_liked_songs(self, limit: int = 100) -> JsonDict:
        """
        Gets playlist items for the 'Liked Songs' playlist

        :param limit: How many items to return. Default: 100
        :return: List of playlistItem dictionaries. See :py:func:`get_playlist`
        """
        return self.get_playlist("LM", limit)

    def get_saved_episodes(self, limit: int = 100) -> JsonDict:
        """
        Gets playlist items for the 'Liked Songs' playlist

        :param limit: How many items to return. Default: 100
        :return: List of playlistItem dictionaries. See :py:func:`get_playlist`
        """
        return self.get_playlist("SE", limit)

    def create_playlist(
        self,
        title: str,
        description: str,
        privacy_status: str = "PRIVATE",
        video_ids: list[str] | None = None,
        source_playlist: str | None = None,
    ) -> str | JsonDict:
        """
        Creates a new empty playlist and returns its id.

        :param title: Playlist title
        :param description: Playlist description
        :param privacy_status: Playlists can be ``PUBLIC``, ``PRIVATE``, or ``UNLISTED``. Default: ``PRIVATE``
        :param video_ids: IDs of songs to create the playlist with
        :param source_playlist: Another playlist whose songs should be added to the new playlist
        :return: ID of the YouTube playlist or full response if there was an error
        """
        self._check_auth()

        invalid_characters = ["<", ">"]  # ytmusic will crash if these are part of the title
        invalid_characters_found = [invalid for invalid in invalid_characters if invalid in title]
        if invalid_characters_found:
            msg = f"{title} contains invalid characters: {', '.join(invalid_characters_found)}"
            raise YTMusicUserError(msg)

        body: JsonDict = {
            "title": title,
            "description": html_to_txt(description),  # YT does not allow HTML tags
            "privacyStatus": privacy_status,
        }
        if video_ids is not None:
            body["videoIds"] = video_ids

        if source_playlist is not None:
            body["sourcePlaylistId"] = source_playlist

        endpoint = "playlist/create"
        response = self._send_request(endpoint, body)
        return response["playlistId"] if "playlistId" in response else response

    def edit_playlist(
        self,
        playlistId: str,
        title: str | None = None,
        description: str | None = None,
        privacyStatus: str | None = None,
        moveItem: str | tuple[str, str] | None = None,
        addPlaylistId: str | None = None,
        addToTop: bool | None = None,
    ) -> str | JsonDict:
        """
        Edit title, description or privacyStatus of a playlist.
        You may also move an item within a playlist or append another playlist to this playlist.

        :param playlistId: Playlist id
        :param title: Optional. New title for the playlist
        :param description: Optional. New description for the playlist
        :param privacyStatus: Optional. New privacy status for the playlist
        :param moveItem: Optional. Move one item before another. Items are specified by setVideoId, which is the
            unique id of this playlist item. See :py:func:`get_playlist`
        :param addPlaylistId: Optional. Id of another playlist to add to this playlist
        :param addToTop: Optional. Change the state of this playlist to add items to the top of the playlist (if True)
            or the bottom of the playlist (if False - this is also the default of a new playlist).
        :return: Status String or full response
        """
        self._check_auth()
        body: JsonDict = {"playlistId": validate_playlist_id(playlistId)}
        actions = []
        if title:
            actions.append({"action": "ACTION_SET_PLAYLIST_NAME", "playlistName": title})

        if description:
            actions.append({"action": "ACTION_SET_PLAYLIST_DESCRIPTION", "playlistDescription": description})

        if privacyStatus:
            actions.append({"action": "ACTION_SET_PLAYLIST_PRIVACY", "playlistPrivacy": privacyStatus})

        if moveItem:
            action = {
                "action": "ACTION_MOVE_VIDEO_BEFORE",
                "setVideoId": moveItem if isinstance(moveItem, str) else moveItem[0],
            }
            if isinstance(moveItem, tuple) and len(moveItem) > 1:
                action["movedSetVideoIdSuccessor"] = moveItem[1]
            actions.append(action)

        if addPlaylistId:
            actions.append({"action": "ACTION_ADD_PLAYLIST", "addedFullListId": addPlaylistId})

        if addToTop:
            actions.append({"action": "ACTION_SET_ADD_TO_TOP", "addToTop": "true"})

        if addToTop is not None:
            actions.append({"action": "ACTION_SET_ADD_TO_TOP", "addToTop": str(addToTop)})

        body["actions"] = actions
        endpoint = "browse/edit_playlist"
        response = self._send_request(endpoint, body)
        return response["status"] if "status" in response else response

    def delete_playlist(self, playlistId: str) -> str | JsonDict:
        """
        Delete a playlist.

        :param playlistId: Playlist id
        :return: Status String or full response
        """
        self._check_auth()
        body = {"playlistId": validate_playlist_id(playlistId)}
        endpoint = "playlist/delete"
        response = self._send_request(endpoint, body)
        return response["status"] if "status" in response else response

    def add_playlist_items(
        self,
        playlistId: str,
        videoIds: list[str] | None = None,
        source_playlist: str | None = None,
        duplicates: bool = False,
    ) -> str | JsonDict:
        """
        Add songs to an existing playlist

        :param playlistId: Playlist id
        :param videoIds: List of Video ids
        :param source_playlist: Playlist id of a playlist to add to the current playlist (no duplicate check)
        :param duplicates: If True, duplicates will be added. If False, an error will be returned if there are duplicates (no items are added to the playlist)
        :return: Status String and a dict containing the new setVideoId for each videoId or full response
        """
        self._check_auth()
        body: JsonDict = {"playlistId": validate_playlist_id(playlistId), "actions": []}
        if not videoIds and not source_playlist:
            raise YTMusicUserError(
                "You must provide either videoIds or a source_playlist to add to the playlist"
            )

        if videoIds:
            for videoId in videoIds:
                action = {"action": "ACTION_ADD_VIDEO", "addedVideoId": videoId}
                if duplicates:
                    action["dedupeOption"] = "DEDUPE_OPTION_SKIP"
                body["actions"].append(action)

        if source_playlist:
            body["actions"].append({"action": "ACTION_ADD_PLAYLIST", "addedFullListId": source_playlist})

            # add an empty ACTION_ADD_VIDEO because otherwise
            # YTM doesn't return the dict that maps videoIds to their new setVideoIds
            if not videoIds:
                body["actions"].append({"action": "ACTION_ADD_VIDEO", "addedVideoId": None})

        endpoint = "browse/edit_playlist"
        response = self._send_request(endpoint, body)
        if "status" in response and "SUCCEEDED" in response["status"]:
            result_dict = [
                result_data.get("playlistEditVideoAddedResultData")
                for result_data in response.get("playlistEditResults", [])
            ]
            return {"status": response["status"], "playlistEditResults": result_dict}
        else:
            return response

    def remove_playlist_items(self, playlistId: str, videos: JsonList) -> str | JsonDict:
        """
        Remove songs from an existing playlist

        :param playlistId: Playlist id
        :param videos: List of PlaylistItems, see :py:func:`get_playlist`.
            Must contain videoId and setVideoId
        :return: Status String or full response
        """
        self._check_auth()
        videos = list(filter(lambda x: "videoId" in x and "setVideoId" in x, videos))
        if len(videos) == 0:
            raise YTMusicUserError(
                "Cannot remove songs, because setVideoId is missing. Do you own this playlist?"
            )

        body: JsonDict = {"playlistId": validate_playlist_id(playlistId), "actions": []}
        for video in videos:
            body["actions"].append(
                {
                    "setVideoId": video["setVideoId"],
                    "removedVideoId": video["videoId"],
                    "action": "ACTION_REMOVE_VIDEO",
                }
            )

        endpoint = "browse/edit_playlist"
        response = self._send_request(endpoint, body)
        return response["status"] if "status" in response else response
