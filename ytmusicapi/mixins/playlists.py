from typing import Dict, Union, Tuple
from ._utils import *

from ytmusicapi.continuations import *
from ytmusicapi.navigation import *
from ytmusicapi.helpers import to_int, sum_total_duration
from ytmusicapi.parsers.playlists import *
from ytmusicapi.parsers.browsing import parse_content_list, parse_playlist


class PlaylistsMixin:

    def get_playlist(self,
                     playlistId: str,
                     limit: int = 100,
                     related: bool = False,
                     suggestions_limit: int = 0) -> Dict:
        """
        Returns a list of playlist items

        :param playlistId: Playlist id
        :param limit: How many songs to return. `None` retrieves them all. Default: 100
        :param related: Whether to fetch 10 related playlists or not. Default: False
        :param suggestions_limit: How many suggestions to return. The result is a list of
            suggested playlist items (videos) contained in a "suggestions" key.
            7 items are retrieved in each internal request. Default: 0
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
        body = {'browseId': browseId}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response,
                      SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + ['musicPlaylistShelfRenderer'])
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
        playlist["description"] = nav(header, DESCRIPTION, True)
        run_count = len(nav(header, SUBTITLE_RUNS))
        if run_count > 1:
            playlist['author'] = {
                'name': nav(header, SUBTITLE2),
                'id': nav(header, SUBTITLE_RUNS + [2] + NAVIGATION_BROWSE_ID, True)
            }
            if run_count == 5:
                playlist['year'] = nav(header, SUBTITLE3)

        playlist['views'] = None
        playlist['duration'] = None
        if 'runs' in header['secondSubtitle']:
            second_subtitle_runs = header['secondSubtitle']['runs']
            has_views = (len(second_subtitle_runs) > 3) * 2
            playlist['views'] = None if not has_views else to_int(second_subtitle_runs[0]['text'])
            has_duration = (len(second_subtitle_runs) > 1) * 2
            playlist['duration'] = None if not has_duration else second_subtitle_runs[has_views + has_duration]['text']
            song_count = second_subtitle_runs[has_views + 0]['text'].split(" ")
            song_count = to_int(song_count[0]) if len(song_count) > 1 else 0
        else:
            song_count = len(results['contents'])

        playlist['trackCount'] = song_count

        request_func = lambda additionalParams: self._send_request(endpoint, body, additionalParams)

        # suggestions and related are missing e.g. on liked songs
        section_list = nav(response, SINGLE_COLUMN_TAB + ['sectionListRenderer'])
        playlist['related'] = []
        if 'continuations' in section_list:
            additionalParams = get_continuation_params(section_list)
            if own_playlist and (suggestions_limit > 0 or related):
                parse_func = lambda results: parse_playlist_items(results)
                suggested = request_func(additionalParams)
                continuation = nav(suggested, SECTION_LIST_CONTINUATION)
                additionalParams = get_continuation_params(continuation)
                suggestions_shelf = nav(continuation, CONTENT + MUSIC_SHELF)
                playlist['suggestions'] = get_continuation_contents(suggestions_shelf, parse_func)

                parse_func = lambda results: parse_playlist_items(results)
                playlist['suggestions'].extend(
                    get_continuations(suggestions_shelf,
                                      'musicShelfContinuation',
                                      suggestions_limit - len(playlist['suggestions']),
                                      request_func,
                                      parse_func,
                                      reloadable=True))

            if related:
                response = request_func(additionalParams)
                continuation = nav(response, SECTION_LIST_CONTINUATION, True)
                if continuation:
                    parse_func = lambda results: parse_content_list(results, parse_playlist)
                    playlist['related'] = get_continuation_contents(
                        nav(continuation, CONTENT + CAROUSEL), parse_func)

        playlist['tracks'] = []
        if 'contents' in results:
            playlist['tracks'] = parse_playlist_items(results['contents'])

            parse_func = lambda contents: parse_playlist_items(contents)
            if 'continuations' in results:
                playlist['tracks'].extend(
                    get_continuations(results, 'musicPlaylistShelfContinuation', limit,
                                      request_func, parse_func))

        playlist['duration_seconds'] = sum_total_duration(playlist)
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
        self._check_auth()
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
        response = self._send_request(endpoint, body)
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
        self._check_auth()
        body = {'playlistId': validate_playlist_id(playlistId)}
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
        response = self._send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def delete_playlist(self, playlistId: str) -> Union[str, Dict]:
        """
        Delete a playlist.

        :param playlistId: Playlist id
        :return: Status String or full response
        """
        self._check_auth()
        body = {'playlistId': validate_playlist_id(playlistId)}
        endpoint = 'playlist/delete'
        response = self._send_request(endpoint, body)
        return response['status'] if 'status' in response else response

    def add_playlist_items(self,
                           playlistId: str,
                           videoIds: List[str] = None,
                           source_playlist: str = None,
                           duplicates: bool = False) -> Union[str, Dict]:
        """
        Add songs to an existing playlist

        :param playlistId: Playlist id
        :param videoIds: List of Video ids
        :param source_playlist: Playlist id of a playlist to add to the current playlist (no duplicate check)
        :param duplicates: If True, duplicates will be added. If False, an error will be returned if there are duplicates (no items are added to the playlist)
        :return: Status String and a dict containing the new setVideoId for each videoId or full response
        """
        self._check_auth()
        body = {'playlistId': validate_playlist_id(playlistId), 'actions': []}
        if not videoIds and not source_playlist:
            raise Exception(
                "You must provide either videoIds or a source_playlist to add to the playlist")

        if videoIds:
            for videoId in videoIds:
                action = {'action': 'ACTION_ADD_VIDEO', 'addedVideoId': videoId}
                if duplicates:
                    action['dedupeOption'] = 'DEDUPE_OPTION_SKIP'
                body['actions'].append(action)

        if source_playlist:
            body['actions'].append({
                'action': 'ACTION_ADD_PLAYLIST',
                'addedFullListId': source_playlist
            })

            # add an empty ACTION_ADD_VIDEO because otherwise
            # YTM doesn't return the dict that maps videoIds to their new setVideoIds
            if not videoIds:
                body['actions'].append({'action': 'ACTION_ADD_VIDEO', 'addedVideoId': None})

        endpoint = 'browse/edit_playlist'
        response = self._send_request(endpoint, body)
        if 'status' in response and 'SUCCEEDED' in response['status']:
            result_dict = [
                result_data.get("playlistEditVideoAddedResultData")
                for result_data in response.get("playlistEditResults", [])
            ]
            return {"status": response["status"], "playlistEditResults": result_dict}
        else:
            return response

    def remove_playlist_items(self, playlistId: str, videos: List[Dict]) -> Union[str, Dict]:
        """
        Remove songs from an existing playlist

        :param playlistId: Playlist id
        :param videos: List of PlaylistItems, see :py:func:`get_playlist`.
            Must contain videoId and setVideoId
        :return: Status String or full response
        """
        self._check_auth()
        videos = list(filter(lambda x: 'videoId' in x and 'setVideoId' in x, videos))
        if len(videos) == 0:
            raise Exception(
                "Cannot remove songs, because setVideoId is missing. Do you own this playlist?")

        body = {'playlistId': validate_playlist_id(playlistId), 'actions': []}
        for video in videos:
            body['actions'].append({
                'setVideoId': video['setVideoId'],
                'removedVideoId': video['videoId'],
                'action': 'ACTION_REMOVE_VIDEO'
            })

        endpoint = 'browse/edit_playlist'
        response = self._send_request(endpoint, body)
        return response['status'] if 'status' in response else response
