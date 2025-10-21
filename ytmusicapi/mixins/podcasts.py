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
        
        # iOS Compatibility: Handle both desktop and mobile formats
        try:
            # Try desktop format first (original implementation)
            two_columns = nav(response, TWO_COLUMN_RENDERER)
            header = nav(two_columns, [*TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
            podcast: JsonDict = parse_podcast_header(header)
            results = nav(two_columns, ["secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF])
        except (KeyError, TypeError):
            # Fall back to mobile format (iOS single-column)
            try:
                single_column = nav(response, SINGLE_COLUMN_TAB)
                sections = nav(single_column, SECTION_LIST)
                
                # Find header section (usually first section with header info)
                header = None
                results = None
                
                for section in sections:
                    if "musicResponsiveHeaderRenderer" in section:
                        header = section["musicResponsiveHeaderRenderer"]
                        podcast: JsonDict = parse_podcast_header(header)
                    elif "musicShelfRenderer" in section:
                        # Found episodes section
                        results = section["musicShelfRenderer"]
                        break
                    elif "musicCarouselShelfRenderer" in section:
                        # Alternative episodes section format
                        carousel = section["musicCarouselShelfRenderer"]
                        if "contents" in carousel:
                            # Convert carousel format to shelf format for compatibility
                            results = {"contents": carousel["contents"]}
                            if "continuations" in carousel:
                                results["continuations"] = carousel["continuations"]
                            break
                
                if header is None:
                    # If no responsive header found, try alternative mobile header locations
                    for section in sections:
                        if "musicDetailHeaderRenderer" in section:
                            header = section["musicDetailHeaderRenderer"]
                            podcast: JsonDict = parse_podcast_header(header)
                            break
                
                if header is None:
                    raise KeyError("Could not find podcast header in mobile format")
                
                if results is None:
                    raise KeyError("Could not find podcast episodes in mobile format")
                
            except (KeyError, TypeError) as mobile_error:
                # If both desktop and mobile parsing fail, raise informative error
                raise KeyError(
                    f"Unable to parse podcast data. Desktop parsing failed, mobile parsing also failed: {mobile_error}. "
                    f"Response structure may have changed or podcast may not be accessible."
                ) from mobile_error
        
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

        # iOS Compatibility: Handle both desktop and mobile formats
        try:
            # Try desktop format first (original implementation)
            two_columns = nav(response, TWO_COLUMN_RENDERER)
            header = nav(two_columns, [*TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
            episode = parse_episode_header(header)

            episode["description"] = None
            description_runs = nav(
                two_columns,
                ["secondaryContents", *SECTION_LIST_ITEM, *DESCRIPTION_SHELF, "description", "runs"],
                True,
            )
            if description_runs:
                episode["description"] = Description.from_runs(description_runs)
        except (KeyError, TypeError):
            # Fall back to mobile format (iOS single-column)
            try:
                single_column = nav(response, SINGLE_COLUMN_TAB)
                sections = nav(single_column, SECTION_LIST)
                
                # Find header section and description section
                header = None
                description_runs = None
                
                for section in sections:
                    if "musicResponsiveHeaderRenderer" in section:
                        header = section["musicResponsiveHeaderRenderer"]
                        episode = parse_episode_header(header)
                    elif "itemSectionRenderer" in section:
                        # Look for description in item section
                        items = section["itemSectionRenderer"].get("contents", [])
                        for item in items:
                            if "elementRenderer" in item:
                                element = item["elementRenderer"]
                                if ("newElement" in element and 
                                    "model" in element["newElement"] and
                                    "musicTextModel" in element["newElement"]["model"]):
                                    # Found description in mobile format
                                    text_model = element["newElement"]["model"]["musicTextModel"]
                                    if "data" in text_model and "formattedTexts" in text_model["data"]:
                                        formatted_texts = text_model["data"]["formattedTexts"]
                                        if len(formatted_texts) > 0:
                                            # Convert mobile format to runs format
                                            formatted_text = formatted_texts[0]
                                            if "commandRuns" in formatted_text:
                                                description_runs = []
                                                content = formatted_text.get("content", "")
                                                command_runs = formatted_text["commandRuns"]
                                                
                                                # Build runs from command runs
                                                last_end = 0
                                                for cmd_run in command_runs:
                                                    start = cmd_run["startIndex"]
                                                    length = cmd_run["length"]
                                                    end = start + length
                                                    
                                                    # Add text before command
                                                    if start > last_end:
                                                        description_runs.append({
                                                            "text": content[last_end:start]
                                                        })
                                                    
                                                    # Add command text with URL if available
                                                    cmd_text = content[start:end]
                                                    run_data = {"text": cmd_text}
                                                    
                                                    if ("onTap" in cmd_run and 
                                                        "innertubeCommand" in cmd_run["onTap"] and
                                                        "urlEndpoint" in cmd_run["onTap"]["innertubeCommand"]):
                                                        run_data["url"] = cmd_run["onTap"]["innertubeCommand"]["urlEndpoint"]["url"]
                                                    elif ("onTap" in cmd_run and 
                                                          "innertubeCommand" in cmd_run["onTap"] and
                                                          "watchEndpoint" in cmd_run["onTap"]["innertubeCommand"]):
                                                        # Handle timestamp links
                                                        watch_endpoint = cmd_run["onTap"]["innertubeCommand"]["watchEndpoint"]
                                                        if "startTimeSeconds" in watch_endpoint:
                                                            run_data["seconds"] = watch_endpoint["startTimeSeconds"]
                                                    
                                                    description_runs.append(run_data)
                                                    last_end = end
                                                
                                                # Add remaining text
                                                if last_end < len(content):
                                                    description_runs.append({
                                                        "text": content[last_end:]
                                                    })
                                                break
                
                if header is None:
                    # Try alternative mobile header locations
                    for section in sections:
                        if "musicDetailHeaderRenderer" in section:
                            header = section["musicDetailHeaderRenderer"]
                            episode = parse_episode_header(header)
                            break
                
                if header is None:
                    raise KeyError("Could not find episode header in mobile format")
                
                # Set description from mobile format
                episode["description"] = None
                if description_runs:
                    episode["description"] = Description.from_runs(description_runs)
                
            except (KeyError, TypeError) as mobile_error:
                # If both desktop and mobile parsing fail, raise informative error
                raise KeyError(
                    f"Unable to parse episode data. Desktop parsing failed, mobile parsing also failed: {mobile_error}. "
                    f"Response structure may have changed or episode may not be accessible."
                ) from mobile_error

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

        # Try desktop format first (TWO_COLUMN_RENDERER)
        results = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION_LIST_ITEM, *MUSIC_SHELF], True)
        
        # If desktop format not found, try iOS mobile format (SINGLE_COLUMN_TAB)
        if results is None:
            results = nav(response, [*SINGLE_COLUMN_TAB, *SECTION_LIST_ITEM, *MUSIC_SHELF], True)
        
        # Final fallback for mobile format without SINGLE_COLUMN_TAB
        if results is None:
            results = nav(response, [*SECTION_LIST_ITEM, *MUSIC_SHELF], True)
        
        if results is None:
            playlist["episodes"] = []
        else:
            parse_func: ParseFuncType = lambda contents: parse_content_list(contents, parse_episode, MMRIR)
            playlist["episodes"] = parse_func(results["contents"])

        return playlist
