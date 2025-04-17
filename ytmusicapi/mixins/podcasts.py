from ytmusicapi.continuations import *
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.navigation import *
from ytmusicapi.parsers.browsing import parse_content_list
from ytmusicapi.parsers.playlists import parse_playlist_header
from ytmusicapi.parsers.podcasts import *
from ytmusicapi.type_alias import JsonDict, JsonList, ParseFuncType, RequestFuncType

from ._utils import *


class PodcastsMixin(MixinProtocol):
    """Podcasts Mixin"""

    def get_channel(self, channelId: str) -> JsonDict:
        """
        Get information about a podcast channel (episodes, podcasts). For episodes, a
        maximum of 10 episodes are returned, the full list of episodes can be retrieved
        via :py:func:`get_channel_episodes`

        :param channelId: channel id
        :return: Dict containing channel info

        Example::

            {
                "title": 'Stanford Graduate School of Business',
                "thumbnails": [...]
                "episodes":
                {
                    "browseId": "UCGwuxdEeCf0TIA2RbPOj-8g",
                    "results":
                    [
                        {
                            "index": 0,
                            "title": "The Brain Gain: The Impact of Immigration on American Innovation with Rebecca Diamond",
                            "description": "Immigrants' contributions to America ...",
                            "duration": "24 min",
                            "videoId": "TS3Ovvk3VAA",
                            "browseId": "MPEDTS3Ovvk3VAA",
                            "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE",
                            "date": "Mar 6, 2024",
                            "thumbnails": [...]
                        },
                    ],
                    "params": "6gPiAUdxWUJXcFlCQ3BN..."
                },
                "podcasts":
                {
                    "browseId": null,
                    "results":
                    [
                        {
                            "title": "Stanford GSB Podcasts",
                            "channel":
                            {
                                "id": "UCGwuxdEeCf0TIA2RbPOj-8g",
                                "name": "Stanford Graduate School of Business"
                            },
                            "browseId": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9",
                            "podcastId": "PLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9",
                            "thumbnails": [...]
                        }
                   ]
                }
            }
        """
        body = {"browseId": channelId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        channel = {
            "title": nav(response, [*HEADER_MUSIC_VISUAL, *TITLE_TEXT]),
            "thumbnails": nav(response, [*HEADER_MUSIC_VISUAL, *THUMBNAILS]),
        }

        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        channel.update(self.parser.parse_channel_contents(results))

        return channel

    def get_channel_episodes(self, channelId: str, params: str) -> JsonList:
        """
        Get all channel episodes. This endpoint is currently unlimited

        :param channelId: channelId of the user
        :param params: params obtained by :py:func:`get_channel`

        :return: List of channel episodes in the format of :py:func:`get_channel` "episodes" key
        """
        body = {"browseId": channelId, "params": params}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + GRID_ITEMS)
        return parse_content_list(results, parse_episode, MMRIR)

    def get_podcast(self, playlistId: str, limit: int | None = 100) -> JsonDict:
        """
        Returns podcast metadata and episodes

        .. note::

            To add a podcast to your library, you need to call ``rate_playlist`` on it

        :param playlistId: Playlist id
        :param limit: How many songs to return. ``None`` retrieves them all. Default: 100
        :return: Dict with podcast information

        Example::

            {
                "author":
                {
                    "name": "Stanford Graduate School of Business",
                    "id": "UCGwuxdEeCf0TIA2RbPOj-8g"
                },
                "title": "Think Fast, Talk Smart: The Podcast",
                "description": "Join Matt Abrahams, a lecturer of...",
                "saved": false,
                "episodes":
                [
                    {
                        "index": 0,
                        "title": "132. Lean Into Failure: How to Make Mistakes That Work | Think Fast, Talk Smart: Communication...",
                        "description": "Effective and productive teams and...",
                        "duration": "25 min",
                        "videoId": "xAEGaW2my7E",
                        "browseId": "MPEDxAEGaW2my7E",
                        "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE",
                        "date": "Mar 5, 2024",
                        "thumbnails": [...]
                    }
                ]
            }
        """
        browseId = "MPSP" + playlistId if not playlistId.startswith("MPSP") else playlistId
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        two_columns = nav(response, TWO_COLUMN_RENDERER)
        header = nav(two_columns, [*TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
        podcast: JsonDict = parse_podcast_header(header)

        results = nav(two_columns, ["secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF])
        parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_episode, MMRIR)
        episodes = parse_func(results["contents"])

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            remaining_limit = None if limit is None else (limit - len(episodes))
            episodes.extend(
                get_continuations(
                    results, "musicShelfContinuation", remaining_limit, request_func, parse_func
                )
            )

        podcast["episodes"] = episodes

        return podcast

    def get_episode(self, videoId: str) -> JsonDict:
        """
        Retrieve episode data for a single episode

        .. note::

           To save an episode, you need to call ``add_playlist_items`` to add
           it to the ``SE`` (saved episodes) playlist.

        :param videoId: browseId (MPED..) or videoId for a single episode
        :return: Dict containing information about the episode

        The description elements are based on a custom dataclass, not shown in the example below
        The description text items also contain "\\n" to indicate newlines, removed below due to RST issues

        Example::

            {
                "author":
                {
                    "name": "Stanford GSB Podcasts",
                    "id": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9"
                },
                "title": "124. Making Meetings Me...",
                "date": "Jan 16, 2024",
                "duration": "25 min",
                "saved": false,
                "playlistId": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9",
                "description":
                [
                    {
                        "text": "Delve into why people hate meetings, ... Karin Reed ("
                    },
                    {
                        "text": "https://speakerdynamics.com/team/",
                        "url": "https://speakerdynamics.com/team/"
                    },
                    {
                        "text": ")Chapters:("
                    },
                    {
                        "text": "00:00",
                        "seconds": 0
                    },
                    {
                        "text": ") Introduction Host Matt Abrahams...("
                    },
                    {
                        "text": "01:30",
                        "seconds": 90
                    },
                ]
            }

        """
        browseId = "MPED" + videoId if not videoId.startswith("MPED") else videoId
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        two_columns = nav(response, TWO_COLUMN_RENDERER)
        header = nav(two_columns, [*TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
        episode = parse_episode_header(header)

        description_runs = nav(
            two_columns, ["secondaryContents", *SECTION_LIST_ITEM, *DESCRIPTION_SHELF, "description", "runs"]
        )
        episode["description"] = Description.from_runs(description_runs)

        return episode

    def get_episodes_playlist(self, playlist_id: str = "RDPN") -> JsonDict:
        """
        Get all episodes in an episodes playlist. Currently the only known playlist is the
        "New Episodes" auto-generated playlist

        :param playlist_id: Playlist ID, defaults to "RDPN", the id of the New Episodes playlist
        :return: Dictionary in the format of :py:func:`get_podcast`
        """
        browseId = "VL" + playlist_id if not playlist_id.startswith("VL") else playlist_id
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        playlist = parse_playlist_header(response)

        results = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF])
        parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_episode, MMRIR)
        playlist["episodes"] = parse_func(results["contents"])

        return playlist
