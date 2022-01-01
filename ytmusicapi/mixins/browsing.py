from ytmusicapi.helpers import *
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.search_params import *
from ytmusicapi.parsers.albums import *
from ytmusicapi.parsers.playlists import *
from ytmusicapi.parsers.library import parse_albums


class BrowsingMixin:
    def search(self,
               query: str,
               filter: str = None,
               scope: str = None,
               limit: int = 20,
               ignore_spelling: bool = False) -> List[Dict]:
        """
        Search YouTube music
        Returns results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``community_playlists``, ``featured_playlists``, ``uploads``.
          Default: Default search, including all types of items.
        :param scope: Search scope. Allowed values: ``library``, ``uploads``.
            Default: Search the public YouTube Music catalogue.
        :param limit: Number of search results to return
          Default: 20
        :param ignore_spelling: Whether to ignore YTM spelling suggestions.
          If True, the exact search term will be searched for, and will not be corrected.
          This does not have any effect when the filter is set to ``uploads``.
          Default: False, will use YTM's default behavior of autocorrecting the search.
        :return: List of results depending on filter.
          resultType specifies the type of item (important for default search).
          albums, artists and playlists additionally contain a browseId, corresponding to
          albumId, channelId and playlistId (browseId=``VL``+playlistId)

          Example list for default search with one result per resultType for brevity. Normally
          there are 3 results per resultType and an additional ``thumbnails`` key::

            [
              {
                "category": "Top result",
                "resultType": "video",
                "videoId": "vU05Eksc_iM",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "1.4M",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Songs",
                "resultType": "song",
                "videoId": "ZrOKjDZOtkA",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "album": {
                  "name": "(What's The Story) Morning Glory? (Remastered)",
                  "id": "MPREb_9nqEki4ZDpp"
                },
                "duration": "4:19",
                "duration_seconds": 259
                "isExplicit": false,
                "feedbackTokens": {
                  "add": null,
                  "remove": null
                }
              },
              {
                "category": "Albums",
                "resultType": "album",
                "browseId": "MPREb_9nqEki4ZDpp",
                "title": "(What's The Story) Morning Glory? (Remastered)",
                "type": "Album",
                "artist": "Oasis",
                "year": "1995",
                "isExplicit": false
              },
              {
                "category": "Community playlists",
                "resultType": "playlist",
                "browseId": "VLPLK1PkWQlWtnNfovRdGWpKffO1Wdi2kvDx",
                "title": "Wonderwall - Oasis",
                "author": "Tate Henderson",
                "itemCount": "174"
              },
              {
                "category": "Videos",
                "resultType": "video",
                "videoId": "bx1Bh8ZvH84",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "386M",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Artists",
                "resultType": "artist",
                "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                "artist": "Oasis",
                "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg",
                "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg"
              }
            ]


        """
        body = {'query': query}
        endpoint = 'search'
        search_results = []
        filters = [
            'albums', 'artists', 'playlists', 'community_playlists', 'featured_playlists', 'songs',
            'videos'
        ]
        if filter and filter not in filters:
            raise Exception(
                "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
                + ', '.join(filters))

        scopes = ['library', 'uploads']
        if scope and scope not in scopes:
            raise Exception(
                "Invalid scope provided. Please use one of the following scopes or leave out the parameter: "
                + ', '.join(scopes))

        params = get_search_params(filter, scope, ignore_spelling)
        if params:
            body['params'] = params

        response = self._send_request(endpoint, body)

        # no results
        if 'contents' not in response:
            return search_results

        if 'tabbedSearchResultsRenderer' in response['contents']:
            tab_index = 0 if not scope or filter else scopes.index(scope) + 1
            results = response['contents']['tabbedSearchResultsRenderer']['tabs'][tab_index][
                'tabRenderer']['content']
        else:
            results = response['contents']

        results = nav(results, SECTION_LIST)

        # no results
        if len(results) == 1 and 'itemSectionRenderer' in results:
            return search_results

        # set filter for parser
        if filter and 'playlists' in filter:
            filter = 'playlists'
        elif scope == scopes[1]:
            filter = scopes[1]

        for res in results:
            if 'musicShelfRenderer' in res:
                results = res['musicShelfRenderer']['contents']
                original_filter = filter
                category = nav(res, MUSIC_SHELF + TITLE_TEXT, True)
                if not filter and scope == scopes[0]:
                    filter = category

                type = filter[:-1].lower() if filter else None
                search_results.extend(self.parser.parse_search_results(results, type, category))
                filter = original_filter

                if 'continuations' in res['musicShelfRenderer']:
                    request_func = lambda additionalParams: self._send_request(
                        endpoint, body, additionalParams)

                    parse_func = lambda contents: self.parser.parse_search_results(
                        contents, type, category)

                    search_results.extend(
                        get_continuations(res['musicShelfRenderer'], 'musicShelfContinuation',
                                          limit - len(search_results), request_func, parse_func))

        return search_results

    def get_artist(self, channelId: str) -> Dict:
        """
        Get information about an artist and their top releases (songs,
        albums, singles, videos, and related artists). The top lists
        contain pointers for getting the full list of releases. For
        songs/videos, pass the browseId to :py:func:`get_playlist`.
        For albums/singles, pass browseId and params to :py:func:
        `get_artist_albums`.

        :param channelId: channel id of the artist
        :return: Dictionary with requested information.

        Example::

            {
                "description": "Oasis were ...",
                "views": "1838795605",
                "name": "Oasis",
                "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q",
                "subscribers": "2.3M",
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
        if channelId.startswith("MPLA"):
            channelId = channelId[4:]
        body = {'browseId': channelId}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)

        if len(results) == 1:
            # not a YouTube Music Channel, a standard YouTube Channel ID with no music content was given
            raise ValueError(f"The YouTube Channel {channelId} has no music content.")

        artist = {'description': None, 'views': None}
        header = response['header']['musicImmersiveHeaderRenderer']
        artist['name'] = nav(header, TITLE_TEXT)
        descriptionShelf = find_object_by_key(results,
                                              'musicDescriptionShelfRenderer',
                                              is_key=True)
        if descriptionShelf:
            artist['description'] = nav(descriptionShelf, DESCRIPTION)
            artist['views'] = None if 'subheader' not in descriptionShelf else descriptionShelf[
                'subheader']['runs'][0]['text']
        subscription_button = header['subscriptionButton']['subscribeButtonRenderer']
        artist['channelId'] = subscription_button['channelId']
        artist['shuffleId'] = nav(header,
                                  ['playButton', 'buttonRenderer'] + NAVIGATION_WATCH_PLAYLIST_ID,
                                  True)
        artist['radioId'] = nav(header, ['startRadioButton', 'buttonRenderer']
                                + NAVIGATION_WATCH_PLAYLIST_ID, True)
        artist['subscribers'] = nav(subscription_button,
                                    ['subscriberCountText', 'runs', 0, 'text'], True)
        artist['subscribed'] = subscription_button['subscribed']
        artist['thumbnails'] = nav(header, THUMBNAILS, True)
        artist['songs'] = {'browseId': None}
        if 'musicShelfRenderer' in results[0]:  # API sometimes does not return songs
            musicShelf = nav(results[0], MUSIC_SHELF)
            if 'navigationEndpoint' in nav(musicShelf, TITLE):
                artist['songs']['browseId'] = nav(musicShelf, TITLE + NAVIGATION_BROWSE_ID)
            artist['songs']['results'] = parse_playlist_items(musicShelf['contents'])

        artist.update(self.parser.parse_artist_contents(results))
        return artist

    def get_artist_albums(self, channelId: str, params: str) -> List[Dict]:
        """
        Get the full list of an artist's albums or singles

        :param channelId: channel Id of the artist
        :param params: params obtained by :py:func:`get_artist`
        :return: List of albums in the format of :py:func:`get_library_albums`,
          except artists key is missing.

        """
        body = {"browseId": channelId, "params": params}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + GRID_ITEMS)
        albums = parse_albums(results)

        return albums

    def get_user(self, channelId: str) -> Dict:
        """
        Retrieve a user's page. A user may own videos or playlists.

        :param channelId: channelId of the user
        :return: Dictionary with information about a user.

        Example::

            {
              "name": "4Tune – No Copyright Music",
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
        endpoint = 'browse'
        body = {"browseId": channelId}
        response = self._send_request(endpoint, body)
        user = {'name': nav(response, ['header', 'musicVisualHeaderRenderer'] + TITLE_TEXT)}
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST)
        user.update(self.parser.parse_artist_contents(results))
        return user

    def get_user_playlists(self, channelId: str, params: str) -> List[Dict]:
        """
        Retrieve a list of playlists for a given user.
        Call this function again with the returned ``params`` to get the full list.

        :param channelId: channelId of the user.
        :param params: params obtained by :py:func:`get_artist`
        :return: List of user playlists in the format of :py:func:`get_library_playlists`

        """
        endpoint = 'browse'
        body = {"browseId": channelId, 'params': params}
        response = self._send_request(endpoint, body)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + GRID_ITEMS)
        user_playlists = parse_content_list(results, parse_playlist)

        return user_playlists

    def get_album_browse_id(self, audioPlaylistId: str):
        """
        Get an album's browseId based on its audioPlaylistId
        :param audioPlaylistId: id of the audio playlist  (starting with `OLAK5uy_`)
        :return: browseId (starting with `MPREb_`)
        """
        params = {"list": audioPlaylistId}
        response = self._send_get_request(YTM_DOMAIN + "/playlist", params)
        matches = re.findall(r"\"MPRE.+?\"", response)
        browse_id = None
        if len(matches) > 0:
            browse_id = matches[0].encode('utf8').decode('unicode-escape').strip('"')
        return browse_id

    def get_album(self, browseId: str) -> Dict:
        """
        Get information and tracks of an album

        :param browseId: browseId of the album, for example
            returned by :py:func:`search`
        :return: Dictionary with album and track metadata.

        Each track is in the following format::

            {
                "title": "Revival",
                "type": "Album",
                "thumbnails": [],
                "description": "Revival is the ninth studio album by American rapper Eminem. ...",
                "artists": [{
                        "name": "Eminem",
                        "id": "UCedvOgsKFzcK3hA5taf3KoQ"
                }],
                "year": "2017",
                "trackCount": 19,
                "duration": "1 hour, 17 minutes",
                "duration_seconds": 4657,
                "audioPlaylistId": "OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY",
                "tracks": [
                    {
                        "videoId": "iKLU7z_xdYQ",
                        "title": "Walk On Water (feat. Beyoncé)",
                        "artists": None,
                        "album": None,
                        "likeStatus": "INDIFFERENT",
                        "thumbnails": None,
                        "isAvailable": True,
                        "isExplicit": True,
                        "duration": "5:03",
                        "feedbackTokens":
                        {
                            "add": "AB9zfpJww...",
                            "remove": "AB9zfpI807..."
                        }
                    }
                ]
            }
        """
        body = {'browseId': browseId}
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        album = parse_album_header(response)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        album['tracks'] = parse_playlist_items(results['contents'])
        album['duration_seconds'] = sum_total_duration(album)

        return album

    def get_song(self, videoId: str, signatureTimestamp: int = None) -> Dict:
        """
        Returns metadata and streaming information about a song or video.

        :param videoId: Video id
        :param signatureTimestamp: Provide the current YouTube signatureTimestamp.
            If not provided a default value will be used, which might result in invalid streaming URLs
        :return: Dictionary with song metadata.

        Example::

            {
                "playabilityStatus": {
                    "status": "OK",
                    "playableInEmbed": true,
                    "audioOnlyPlayability": {
                        "audioOnlyPlayabilityRenderer": {
                            "trackingParams": "CAEQx2kiEwiuv9X5i5H1AhWBvlUKHRoZAHk=",
                            "audioOnlyAvailability": "FEATURE_AVAILABILITY_ALLOWED"
                        }
                    },
                    "miniplayer": {
                        "miniplayerRenderer": {
                            "playbackMode": "PLAYBACK_MODE_ALLOW"
                        }
                    },
                    "contextParams": "Q0FBU0FnZ0M="
                },
                "streamingData": {
                    "expiresInSeconds": "21540",
                    "adaptiveFormats": [
                        {
                            "itag": 140,
                            "url": "https://rr1---sn-h0jelnez.c.youtube.com/videoplayback?expire=1641080272...",
                            "mimeType": "audio/mp4; codecs=\"mp4a.40.2\"",
                            "bitrate": 131007,
                            "initRange": {
                                "start": "0",
                                "end": "667"
                            },
                            "indexRange": {
                                "start": "668",
                                "end": "999"
                            },
                            "lastModified": "1620321966927796",
                            "contentLength": "3967382",
                            "quality": "tiny",
                            "projectionType": "RECTANGULAR",
                            "averageBitrate": 129547,
                            "highReplication": true,
                            "audioQuality": "AUDIO_QUALITY_MEDIUM",
                            "approxDurationMs": "245000",
                            "audioSampleRate": "44100",
                            "audioChannels": 2,
                            "loudnessDb": -1.3000002
                        }
                    ]
                },
                "videoDetails": {
                    "videoId": "AjXQiKP5kMs",
                    "title": "Sparks",
                    "lengthSeconds": "245",
                    "channelId": "UCvCk2zFqkCYzpnSgWfx0qOg",
                    "isOwnerViewing": false,
                    "isCrawlable": false,
                    "thumbnail": {
                        "thumbnails": []
                    },
                    "allowRatings": true,
                    "viewCount": "12",
                    "author": "Thomas Bergersen",
                    "isPrivate": true,
                    "isUnpluggedCorpus": false,
                    "musicVideoType": "MUSIC_VIDEO_TYPE_PRIVATELY_OWNED_TRACK",
                    "isLiveContent": false
                },
                "microformat": {
                    "microformatDataRenderer": {
                        "urlCanonical": "https://music.youtube.com/watch?v=AjXQiKP5kMs",
                        "title": "Sparks - YouTube Music",
                        "description": "Uploaded to YouTube via YouTube Music Sparks",
                        "thumbnail": {
                            "thumbnails": [
                                {
                                    "url": "https://i.ytimg.com/vi/AjXQiKP5kMs/hqdefault.jpg",
                                    "width": 480,
                                    "height": 360
                                }
                            ]
                        },
                        "siteName": "YouTube Music",
                        "appName": "YouTube Music",
                        "androidPackage": "com.google.android.apps.youtube.music",
                        "iosAppStoreId": "1017492454",
                        "iosAppArguments": "https://music.youtube.com/watch?v=AjXQiKP5kMs",
                        "ogType": "video.other",
                        "urlApplinksIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks",
                        "urlApplinksAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks",
                        "urlTwitterIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link",
                        "urlTwitterAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link",
                        "twitterCardType": "player",
                        "twitterSiteHandle": "@YouTubeMusic",
                        "schemaDotOrgType": "http://schema.org/VideoObject",
                        "noindex": true,
                        "unlisted": true,
                        "paid": false,
                        "familySafe": true,
                        "pageOwnerDetails": {
                            "name": "Music Library Uploads",
                            "externalChannelId": "UCvCk2zFqkCYzpnSgWfx0qOg",
                            "youtubeProfileUrl": "http://www.youtube.com/channel/UCvCk2zFqkCYzpnSgWfx0qOg"
                        },
                        "videoDetails": {
                            "externalVideoId": "AjXQiKP5kMs",
                            "durationSeconds": "246",
                            "durationIso8601": "PT4M6S"
                        },
                        "linkAlternates": [
                            {
                                "hrefUrl": "android-app://com.google.android.youtube/http/youtube.com/watch?v=AjXQiKP5kMs"
                            },
                            {
                                "hrefUrl": "ios-app://544007664/http/youtube.com/watch?v=AjXQiKP5kMs"
                            },
                            {
                                "hrefUrl": "https://www.youtube.com/oembed?format=json&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs",
                                "title": "Sparks",
                                "alternateType": "application/json+oembed"
                            },
                            {
                                "hrefUrl": "https://www.youtube.com/oembed?format=xml&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs",
                                "title": "Sparks",
                                "alternateType": "text/xml+oembed"
                            }
                        ],
                        "viewCount": "12",
                        "publishDate": "1969-12-31",
                        "category": "Music",
                        "uploadDate": "1969-12-31"
                    }
                }
            }

        """
        endpoint = 'player'
        if not signatureTimestamp:
            signatureTimestamp = get_datestamp() - 1

        params = {
            "playbackContext": {
                "contentPlaybackContext": {
                    "signatureTimestamp": signatureTimestamp
                }
            },
            "video_id": videoId
        }
        response = self._send_request(endpoint, params)
        keys = ['videoDetails', 'playabilityStatus', 'streamingData', 'microformat']
        for k in list(response.keys()):
            if k not in keys:
                del response[k]
        return response

    def get_lyrics(self, browseId: str) -> Dict:
        """
        Returns lyrics of a song or video.

        :param browseId: Lyrics browse id obtained from `get_watch_playlist`
        :return: Dictionary with song lyrics.

        Example::

            {
                "lyrics": "Today is gonna be the day\\nThat they're gonna throw it back to you\\n",
                "source": "Source: LyricFind"
            }

        """
        lyrics = {}
        if not browseId:
            raise Exception("Invalid browseId provided. This song might not have lyrics.")

        response = self._send_request('browse', {'browseId': browseId})
        lyrics['lyrics'] = nav(response, ['contents'] + SECTION_LIST_ITEM
                               + ['musicDescriptionShelfRenderer'] + DESCRIPTION, True)
        lyrics['source'] = nav(response, ['contents'] + SECTION_LIST_ITEM
                               + ['musicDescriptionShelfRenderer', 'footer'] + RUN_TEXT, True)

        return lyrics

    def get_basejs_url(self):
        """
        Extract the URL for the `base.js` script from YouTube Music.

        :return: URL to `base.js`
        """
        response = self._send_get_request(url=YTM_DOMAIN)
        match = re.search(r'jsUrl"\s*:\s*"([^"]+)"', response)
        if match is None:
            raise Exception("Could not identify the URL for base.js player.")

        return YTM_DOMAIN + match.group(1)

    def get_signatureTimestamp(self, url: str = None) -> int:
        """
        Fetch the `base.js` script from YouTube Music and parse out the
        `signatureTimestamp` for use with :py:func:`get_song`.

        :param url: Optional. Provide the URL of the `base.js` script. If this
            isn't specified a call will be made to :py:func:`get_basejs_url`.
        :return: `signatureTimestamp` string
        """
        if url is None:
            url = self.get_basejs_url()
        response = self._send_get_request(url=url)
        match = re.search(r"signatureTimestamp[:=](\d+)", response)
        if match is None:
            raise Exception("Unable to identify the signatureTimestamp.")

        return int(match.group(1))
