from typing import Dict

from ytmusicapi.continuations import *
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.navigation import *
from ytmusicapi.parsers.podcasts import *

from ._utils import *


class PodcastsMixin(MixinProtocol):
    def get_podcast(self, playlistId: str, limit: Optional[int] = 100) -> Dict:
        """
        Returns podcast metadata and episodes

        .. note::

            To add a podcast to your library, you need to call `rate_playlist` on it

        :param playlistId: Playlist id
        :param limit: How many songs to return. `None` retrieves them all. Default: 100
        """
        browseId = "MPSP" + playlistId if not playlistId.startswith("MPSP") else playlistId
        body = {"browseId": browseId}
        endpoint = "browse"
        response = self._send_request(endpoint, body)
        two_columns = nav(response, TWO_COLUMN_RENDERER)
        header = nav(two_columns, [*TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
        podcast = parse_podcast_header(header)

        results = nav(two_columns, ["secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF])
        episodes = parse_episodes(results["contents"])

        if "continuations" in results:
            request_func = lambda additionalParams: self._send_request(endpoint, body, additionalParams)
            parse_func = lambda contents: parse_episodes(contents)
            remaining_limit = None if limit is None else (limit - len(episodes))
            episodes.extend(
                get_continuations(
                    results, "musicShelfContinuation", remaining_limit, request_func, parse_func
                )
            )

        podcast["episodes"] = episodes

        return podcast

    def get_episode(self, videoId: str) -> Dict:
        """
        Retrieve episode data for a single episode

        .. note::

            To save an episode, you need to call `add_playlist_items` to add
            it to the `SE` (saved episodes) playlist.

        :param videoId: browseId (MPED..) or videoId for a single episode
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
