from typing import Literal, cast, overload

from ytmusicapi.enums import ProfileTypes
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.navigation import (
    DESCRIPTION,
    DESCRIPTION_SHELF,
    HEADER_MUSIC_VISUAL,
    MUSIC_SHELF,
    NAVIGATION_BROWSE_ID,
    NAVIGATION_PLAYLIST_ID,
    SECTION_LIST,
    SINGLE_COLUMN_TAB,
    THUMBNAILS,
    TITLE,
    TITLE_TEXT,
    find_object_by_key,
    nav,
)
from ytmusicapi.parsers.playlists import parse_playlist_items
from ytmusicapi.type_alias import ArtistResourceInfo, ChannelResourceInfo, JsonDict, UserResourceInfo


class ResourceMixin(MixinProtocol):
    @overload
    def get_profile(
        self, profile_id: str, profile_type: Literal[ProfileTypes.ARTIST]
    ) -> tuple[Literal[ProfileTypes.ARTIST], ArtistResourceInfo]: ...

    @overload
    def get_profile(
        self, profile_id: str, profile_type: Literal[ProfileTypes.USER]
    ) -> tuple[Literal[ProfileTypes.USER], UserResourceInfo]: ...

    @overload
    def get_profile(
        self, profile_id: str, profile_type: Literal[ProfileTypes.CHANNEL]
    ) -> tuple[Literal[ProfileTypes.CHANNEL], ChannelResourceInfo]: ...

    @overload
    def get_profile(
        self, profile_id: str
    ) -> (
        tuple[Literal[ProfileTypes.ARTIST], ArtistResourceInfo]
        | tuple[Literal[ProfileTypes.USER], UserResourceInfo]
        | tuple[Literal[ProfileTypes.CHANNEL], ChannelResourceInfo]
    ): ...

    def get_profile(
        self, profile_id: str, profile_type: ProfileTypes | None = None
    ) -> (
        tuple[Literal[ProfileTypes.ARTIST], ArtistResourceInfo]
        | tuple[Literal[ProfileTypes.USER], UserResourceInfo]
        | tuple[Literal[ProfileTypes.CHANNEL], ChannelResourceInfo]
    ):
        """
        Get information about a profile page (artist, user, or podcast channel).
        If `profile_type` is not provided, it will be determined based on the response data.
        For detailed information regarding the different profile types data, see
        :py:func:`get_artist`, :py:func:`get_user` and :py:func:`get_channel`.

        :param profile_id: profile_id to retrieve
        :param profile_type: a profile type to interpret the response data as.
            If not provided, it will be determined based on the response.
        :return: tuple of profile type and profile data.
        """
        if profile_id.startswith("MPLA"):
            profile_id = profile_id[4:]
        body = {"browseId": profile_id}
        endpoint = "browse"
        response = self._send_request(endpoint, body)

        if profile_type is None:
            profile_type = self._determine_profile_type(response)

        match profile_type:
            case ProfileTypes.ARTIST:
                return ProfileTypes.ARTIST, self._parse_artist(response)
            case ProfileTypes.USER:
                return ProfileTypes.USER, self._parse_user(response)
            case ProfileTypes.CHANNEL:
                return ProfileTypes.CHANNEL, self._parse_channel(response)
            case _:
                raise ValueError(f"Unknown resource type: {profile_type}")

    def get_artist(self, channelId: str) -> ArtistResourceInfo:
        """
        Get information about an artist and their top releases (songs,
        albums, singles, videos, and related artists). The top lists
        contain pointers for getting the full list of releases.

        Possible content types for get_artist are:

            - songs
            - albums
            - singles
            - shows
            - videos
            - episodes
            - podcasts
            - related

        Each of these content keys in the response contains
        ``results`` and possibly ``browseId`` and ``params``.

        - For songs/videos, pass the browseId to :py:func:`get_playlist`.
        - For albums/singles/shows, pass browseId and params to :py:func:`get_artist_albums`.

        :param channelId: channel id of the artist
        :return: Dictionary with requested information.

        .. warning::

            The returned channelId is not the same as the one passed to the function.
            It should be used only with :py:func:`subscribe_artists`.

        Example::

            {
                "description": "Oasis were ...",
                "views": "3,693,390,359 views",
                "name": "Oasis",
                "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q",
                "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg",
                "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg",
                "subscribers": "3.86M",
                "monthlyListeners": "29.1M",
                "subscribed": false,
                "thumbnails": [...],
                "songs": {
                    "browseId": "VLPLMpM3Z0118S42R1npOhcjoakLIv1aqnS1",
                    "results": [
                        {
                            "videoId": "ZrOKjDZOtkA",
                            "title": "Wonderwall (Remastered)",
                            "thumbnails": [...],
                            "artist": "Oasis",
                            "album": "(What's The Story) Morning Glory? (Remastered)"
                        }
                    ]
                },
                "albums": {
                    "results": [
                        {
                            "title": "Familiar To Millions",
                            "thumbnails": [...],
                            "year": "2018",
                            "browseId": "MPREb_AYetWMZunqA"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "singles": {
                    "results": [
                        {
                            "title": "Stand By Me (Mustique Demo)",
                            "thumbnails": [...],
                            "year": "2016",
                            "browseId": "MPREb_7MPKLhibN5G"
                        }
                    ],
                    "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "params": "6gPTAUNwc0JDbndLYlFBQV..."
                },
                "videos": {
                    "results": [
                        {
                            "title": "Wonderwall",
                            "thumbnails": [...],
                            "views": "358M",
                            "videoId": "bx1Bh8ZvH84",
                            "playlistId": "PLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                        }
                    ],
                    "browseId": "VLPLMpM3Z0118S5xuNckw1HUcj1D021AnMEB"
                },
                "related": {
                    "results": [
                        {
                            "browseId": "UCt2KxZpY5D__kapeQ8cauQw",
                            "subscribers": "450K",
                            "title": "The Verve"
                        },
                        {
                            "browseId": "UCwK2Grm574W1u-sBzLikldQ",
                            "subscribers": "341K",
                            "title": "Liam Gallagher"
                        },
                        ...
                    ]
                }
            }
        """
        _, artist = self.get_profile(channelId, ProfileTypes.ARTIST)
        return artist

    def get_user(self, channelId: str) -> UserResourceInfo:
        """
        Retrieve a user's page. A user may own videos or playlists.

        Use :py:func:`get_user_playlists` to retrieve all playlists::

            result = get_user(channelId)
            get_user_playlists(channelId, result["playlists"]["params"])

        Similarly, use :py:func:`get_user_videos` to retrieve all videos::

            get_user_videos(channelId, result["videos"]["params"])

        :param channelId: channelId of the user
        :return: Dictionary with information about a user.

        Example::

            {
              "name": "4Tune - No Copyright Music",
              "videos": {
                "browseId": "UC44hbeRoCZVVMVg5z0FfIww",
                "results": [
                  {
                    "title": "Epic Music Soundtracks 2019",
                    "videoId": "bJonJjgS2mM",
                    "playlistId": "RDAMVMbJonJjgS2mM",
                    "thumbnails": [
                      {
                        "url": "https://i.ytimg.com/vi/bJon...",
                        "width": 800,
                        "height": 450
                      }
                    ],
                    "views": "19K"
                  }
                ]
              },
              "playlists": {
                "browseId": "UC44hbeRoCZVVMVg5z0FfIww",
                "results": [
                  {
                    "title": "♚ Machinimasound | Playlist",
                    "playlistId": "PLRm766YvPiO9ZqkBuEzSTt6Bk4eWIr3gB",
                    "thumbnails": [
                      {
                        "url": "https://i.ytimg.com/vi/...",
                        "width": 400,
                        "height": 225
                      }
                    ]
                  }
                ],
                "params": "6gO3AUNvWU..."
              }
            }
        """
        _, user = self.get_profile(channelId, ProfileTypes.USER)
        return user

    def get_channel(self, channelId: str) -> ChannelResourceInfo:
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
        _, channel = self.get_profile(channelId, ProfileTypes.CHANNEL)
        return channel

    def _parse_artist(self, data: JsonDict) -> ArtistResourceInfo:
        results = nav(data, SINGLE_COLUMN_TAB + SECTION_LIST)

        artist: JsonDict = {"description": None, "views": None}
        header = data["header"]["musicImmersiveHeaderRenderer"]
        artist["name"] = nav(header, TITLE_TEXT)
        descriptionShelf = find_object_by_key(results, DESCRIPTION_SHELF[0], is_key=True)
        if descriptionShelf:
            artist["description"] = nav(descriptionShelf, DESCRIPTION)
            artist["views"] = (
                None
                if "subheader" not in descriptionShelf
                else descriptionShelf["subheader"]["runs"][0]["text"]
            )
        subscription_button = header["subscriptionButton"]["subscribeButtonRenderer"]
        artist["channelId"] = subscription_button["channelId"]
        artist["shuffleId"] = nav(header, ["playButton", "buttonRenderer", *NAVIGATION_PLAYLIST_ID], True)
        artist["radioId"] = nav(header, ["startRadioButton", "buttonRenderer", *NAVIGATION_PLAYLIST_ID], True)
        artist["subscribers"] = nav(subscription_button, ["subscriberCountText", "runs", 0, "text"], True)
        artist["monthlyListeners"] = nav(header, ["monthlyListenerCount", "runs", 0, "text"], True)
        artist["monthlyListeners"] = (
            artist["monthlyListeners"].replace(" monthly audience", "")
            if artist["monthlyListeners"]
            else None
        )
        artist["subscribed"] = subscription_button["subscribed"]
        artist["thumbnails"] = nav(header, THUMBNAILS, True)
        artist["songs"] = {"browseId": None}
        if "musicShelfRenderer" in results[0]:  # API sometimes does not return songs
            musicShelf = nav(results[0], MUSIC_SHELF)
            if "navigationEndpoint" in nav(musicShelf, TITLE):
                artist["songs"]["browseId"] = nav(musicShelf, TITLE + NAVIGATION_BROWSE_ID)
            artist["songs"]["results"] = parse_playlist_items(musicShelf["contents"])

        artist.update(self.parser.parse_channel_contents(results))
        return cast(ArtistResourceInfo, artist)

    def _parse_user(self, data: JsonDict) -> UserResourceInfo:
        user = {"name": nav(data, [*HEADER_MUSIC_VISUAL, *TITLE_TEXT])}
        results = nav(data, SINGLE_COLUMN_TAB + SECTION_LIST)
        user.update(self.parser.parse_channel_contents(results))
        return cast(UserResourceInfo, user)

    def _parse_channel(self, data: JsonDict) -> ChannelResourceInfo:
        channel = {
            "title": nav(data, [*HEADER_MUSIC_VISUAL, *TITLE_TEXT]),
            "thumbnails": nav(data, [*HEADER_MUSIC_VISUAL, *THUMBNAILS]),
        }

        results = nav(data, SINGLE_COLUMN_TAB + SECTION_LIST)
        channel.update(self.parser.parse_channel_contents(results))

        return cast(ChannelResourceInfo, channel)

    def _determine_profile_type(self, data: JsonDict) -> ProfileTypes:
        response_header = data["header"]
        if "musicImmersiveHeaderRenderer" in response_header:
            return ProfileTypes.ARTIST

        visual_header = response_header["musicVisualHeaderRenderer"]
        if "menu" in visual_header:
            return ProfileTypes.USER

        return ProfileTypes.CHANNEL
