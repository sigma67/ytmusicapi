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
                "duration": "4:38"
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
                "duration": "4:38"
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
            'albums', 'artists', 'playlists', 'community_playlists', 'featured_playlists', 'songs', 'videos'
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
            results = response['contents']['tabbedSearchResultsRenderer']['tabs'][tab_index]['tabRenderer']['content']
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

                    parse_func = lambda contents: self.parser.parse_search_results(contents, type, category)

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
        :return: Dictionary with title, description, artist and tracks.

        Each track is in the following format::

            {
              "title": "Seven",
              "trackCount": "7",
              "durationMs": "1439579",
              "playlistId": "OLAK5uy_kGnhwT08mQMGw8fArBowdtlew3DpgUt9c",
              "releaseDate": {
                "year": 2016,
                "month": 10,
                "day": 28
              },
              "description": "Seven is ...",
              "thumbnails": [...],
              "artists": [
                {
                  "name": "Martin Garrix",
                  "id": "UCqJnSdHjKtfsrHi9aI-9d3g"
                }
              ],
              "tracks": [
                {
                  "index": "1",
                  "title": "WIEE (feat. Mesto)",
                  "artist": "Martin Garrix",
                  "videoId": "8xMNeXI9wxI",
                  "lengthMs": "203406",
                  "likeStatus": "INDIFFERENT"
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
              "videoDetails": {
                "allowRatings": true,
                "author": "Oasis - Topic",
                "averageRating": 4.5783687,
                "channelId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                "isCrawlable": true,
                "isLiveContent": false,
                "isOwnerViewing": false,
                "isPrivate": false,
                "isUnpluggedCorpus": false,
                "lengthSeconds": "259",
                "musicVideoType": "MUSIC_VIDEO_TYPE_ATV",
                "thumbnail": {
                  "thumbnails": [...]
                },
                "title": "Wonderwall",
                "videoId": "ZrOKjDZOtkA",
                "viewCount": "27429003"
              },
              "microformat": {
                "microformatDataRenderer": {
                  "androidPackage": "com.google.android.apps.youtube.music",
                  "appName": "YouTube Music",
                  "availableCountries": ["AE",...],
                  "category": "Music",
                  "description": "Provided to YouTube by Ignition Wonderwall · Oasis ...",
                  "familySafe": true,
                  "iosAppArguments": "https://music.youtube.com/watch?v=ZrOKjDZOtkA",
                  "iosAppStoreId": "1017492454",
                  "linkAlternates": [
                    {
                      "hrefUrl": "android-app://com.google.android.youtube/http/youtube.com/watch?v=ZrOKjDZOtkA"
                    },
                    {
                      "hrefUrl": "ios-app://544007664/http/youtube.com/watch?v=ZrOKjDZOtkA"
                    },
                    {
                      "alternateType": "application/json+oembed",
                      "hrefUrl": "https://www.youtube.com/oembed?format=json&url=...",
                      "title": "Wonderwall (Remastered)"
                    },
                    {
                      "alternateType": "text/xml+oembed",
                      "hrefUrl": "https://www.youtube.com/oembed?format=xml&url=...",
                      "title": "Wonderwall (Remastered)"
                    }
                  ],
                  "noindex": false,
                  "ogType": "video.other",
                  "pageOwnerDetails": {
                    "externalChannelId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                    "name": "Oasis - Topic",
                    "youtubeProfileUrl": "http://www.youtube.com/channel/UCmMUZbaYdNH0bEd1PAlAqsA"
                  },
                  "paid": false,
                  "publishDate": "2017-01-25",
                  "schemaDotOrgType": "http://schema.org/VideoObject",
                  "siteName": "YouTube Music",
                  "tags": ["Oasis",...],
                  "thumbnail": {
                    "thumbnails": [
                      {
                        "height": 720,
                        "url": "https://i.ytimg.com/vi/ZrOKjDZOtkA/maxresdefault.jpg",
                        "width": 1280
                      }
                    ]
                  },
                  "title": "Wonderwall (Remastered) - YouTube Music",
                  "twitterCardType": "player",
                  "twitterSiteHandle": "@YouTubeMusic",
                  "unlisted": false,
                  "uploadDate": "2017-01-25",
                  "urlApplinksAndroid": "vnd.youtube.music://music.youtube.com/watch?v=ZrOKjDZOtkA&feature=applinks",
                  "urlApplinksIos": "vnd.youtube.music://music.youtube.com/watch?v=ZrOKjDZOtkA&feature=applinks",
                  "urlCanonical": "https://music.youtube.com/watch?v=ZrOKjDZOtkA",
                  "urlTwitterAndroid": "vnd.youtube.music://music.youtube.com/watch?v=ZrOKjDZOtkA&feature=twitter-deep-link",
                  "urlTwitterIos": "vnd.youtube.music://music.youtube.com/watch?v=ZrOKjDZOtkA&feature=twitter-deep-link",
                  "videoDetails": {
                    "durationIso8601": "PT4M19S",
                    "durationSeconds": "259",
                    "externalVideoId": "ZrOKjDZOtkA"
                  },
                  "viewCount": "27429003"
                }
              },
              "playabilityStatus": {
                "contextParams": "Q0FFU0FnZ0I=",
                "miniplayer": {
                  "miniplayerRenderer": {
                    "playbackMode": "PLAYBACK_MODE_ALLOW"
                  }
                },
                "playableInEmbed": true,
                "status": "OK"
              },
              "streamingData": {
                "adaptiveFormats": [
                  {
                    "approxDurationMs": "258760",
                    "averageBitrate": 178439,
                    "bitrate": 232774,
                    "contentLength": "5771637",
                    "fps": 25,
                    "height": 1080,
                    "indexRange": {
                      "end": "1398",
                      "start": "743"
                    },
                    "initRange": {
                      "end": "742",
                      "start": "0"
                    },
                    "itag": 137,
                    "lastModified": "1614620567944400",
                    "mimeType": "video/mp4; codecs=\"avc1.640020\"",
                    "projectionType": "RECTANGULAR",
                    "quality": "hd1080",
                    "qualityLabel": "1080p",
                    "signatureCipher": "s=_xxxOq0QJ8...",
                    "width": 1078
                  }[...]
                ],
                "expiresInSeconds": "21540",
                "formats": [
                  {
                    "approxDurationMs": "258809",
                    "audioChannels": 2,
                    "audioQuality": "AUDIO_QUALITY_LOW",
                    "audioSampleRate": "44100",
                    "averageBitrate": 179462,
                    "bitrate": 179496,
                    "contentLength": "5805816",
                    "fps": 25,
                    "height": 360,
                    "itag": 18,
                    "lastModified": "1614620870611066",
                    "mimeType": "video/mp4; codecs=\"avc1.42001E, mp4a.40.2\"",
                    "projectionType": "RECTANGULAR",
                    "quality": "medium",
                    "qualityLabel": "360p",
                    "signatureCipher": "s=kXXXOq0QJ8...",
                    "width": 360
                  }
                ]
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
