import requests
import json
import codecs
from urllib.parse import parse_qs
from typing import List, Dict
from ytmusicapi.helpers import *
from ytmusicapi.parsers.browsing import *
from ytmusicapi.parsers.albums import *
from ytmusicapi.parsers.playlists import *
from ytmusicapi.parsers.library import parse_albums


class BrowsingMixin:
    def search(self,
               query: str,
               filter: str = None,
               limit: int = 20,
               ignore_spelling: bool = False) -> List[Dict]:
        """
        Search YouTube music
        Returns results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``uploads``.
          Default: Default search, including all types of items.
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
                "resultType": "album",
                "browseId": "MPREb_9nqEki4ZDpp",
                "title": "(What's The Story) Morning Glory? (Remastered)",
                "type": "Album",
                "artist": "Oasis",
                "year": "1995",
                "isExplicit": false
              },
              {
                "resultType": "playlist",
                "browseId": "VLPLK1PkWQlWtnNfovRdGWpKffO1Wdi2kvDx",
                "title": "Wonderwall - Oasis",
                "author": "Tate Henderson",
                "itemCount": "174"
              },
              {
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
        filters = ['albums', 'artists', 'playlists', 'songs', 'videos', 'uploads']
        if filter and filter not in filters:
            raise Exception(
                "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
                + ', '.join(filters))

        if filter:
            param1 = 'Eg-KAQwIA'

            if not ignore_spelling:
                param3 = 'MABqChAEEAMQCRAFEAo%3D'
            else:
                param3 = 'MABCAggBagoQBBADEAkQBRAK'

            if filter == 'uploads':
                params = 'agIYAw%3D%3D'
            else:
                if filter == 'videos':
                    param2 = 'BABGAAgACgA'
                elif filter == 'albums':
                    param2 = 'BAAGAEgACgA'
                elif filter == 'artists':
                    param2 = 'BAAGAAgASgA'
                elif filter == 'playlists':
                    param2 = 'BAAGAAgACgB'
                elif filter == 'uploads':
                    self.__check_auth()
                    param2 = 'RABGAEgASgB'
                else:
                    param2 = 'RAAGAAgACgA'
                params = param1 + param2 + param3

            body['params'] = params
        elif ignore_spelling:
            body['params'] = "QgIIAQ%3D%3D"

        response = self._send_request(endpoint, body)

        # no results
        if 'contents' not in response:
            return search_results

        if 'tabbedSearchResultsRenderer' in response['contents']:
            results = response['contents']['tabbedSearchResultsRenderer']['tabs'][int(
                filter == "uploads")]['tabRenderer']['content']
        else:
            results = response['contents']

        results = nav(results, SECTION_LIST)

        # no results
        if len(results) == 1 and 'itemSectionRenderer' in results:
            return search_results

        for res in results:
            if 'musicShelfRenderer' in res:
                results = res['musicShelfRenderer']['contents']

                type = filter[:-1] if filter else None
                search_results.extend(self.parser.parse_search_results(results, type))

                if 'continuations' in res['musicShelfRenderer']:
                    request_func = lambda additionalParams: self._send_request(
                        endpoint, body, additionalParams)

                    parse_func = lambda contents: self.parser.parse_search_results(contents, type)

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
        body = prepare_browse_endpoint("ARTIST", channelId)
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
            artist['description'] = descriptionShelf['description']['runs'][0]['text']
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
        endpoint = "https://music.youtube.com/playlist"
        params = {"list": audioPlaylistId}
        response = requests.get(endpoint, params, headers=self.headers, proxies=self.proxies)
        matches = re.findall(r"\"MPRE.+?\"", response.text)
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
              "artist": [
                {
                  "name": "Martin Garrix",
                  "id": "UCqJnSdHjKtfsrHi9aI-9d3g"
                }
              ],
              "tracks": [
                {
                  "index": "1",
                  "title": "WIEE (feat. Mesto)",
                  "artists": "Martin Garrix",
                  "videoId": "8xMNeXI9wxI",
                  "lengthMs": "203406",
                  "likeStatus": "INDIFFERENT"
                }
              ]
            }
        """
        body = prepare_browse_endpoint("ALBUM", browseId)
        endpoint = 'browse'
        response = self._send_request(endpoint, body)
        album = {}
        data = nav(response, FRAMEWORK_MUTATIONS, True)
        if not data:
            album = parse_album_header(response)
            results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
            album['tracks'] = parse_playlist_items(results['contents'])
        else:
            album_data = find_object_by_key(data, 'musicAlbumRelease', 'payload', True)
            album['title'] = album_data['title']
            album['trackCount'] = album_data['trackCount']
            album['durationMs'] = album_data['durationMs']
            album['playlistId'] = album_data['audioPlaylistId']
            album['releaseDate'] = album_data['releaseDate']
            album['description'] = find_object_by_key(data, 'musicAlbumReleaseDetail', 'payload',
                                                      True)['description']
            album['thumbnails'] = album_data['thumbnailDetails']['thumbnails']
            album['artist'] = []
            artists_data = find_objects_by_key(data, 'musicArtist', 'payload')
            for artist in artists_data:
                album['artist'].append({
                    'name': artist['musicArtist']['name'],
                    'id': artist['musicArtist']['externalChannelId']
                })
            album['tracks'] = []

            track_library_details = {}
            for item in data:
                if 'musicTrackUserDetail' in item['payload']:
                    like_state = item['payload']['musicTrackUserDetail']['likeState'].split(
                        '_')[-1]
                    parent_track = item['payload']['musicTrackUserDetail']['parentTrack']
                    like_state = 'INDIFFERENT' if like_state in ['NEUTRAL', 'UNKNOWN'
                                                                 ] else like_state[:-1]
                    track_library_details[parent_track] = like_state

                if 'musicLibraryEdit' in item['payload']:
                    entity_key = item['entityKey']
                    track_library_details[entity_key] = {
                        'add': item['payload']['musicLibraryEdit']['addToLibraryFeedbackToken'],
                        'remove':
                        item['payload']['musicLibraryEdit']['removeFromLibraryFeedbackToken']
                    }

            for item in data[3:]:
                if 'musicTrack' in item['payload']:
                    music_track = item['payload']['musicTrack']
                    track = {}
                    track['index'] = music_track['albumTrackIndex']
                    track['title'] = music_track['title']
                    track['thumbnails'] = music_track['thumbnailDetails']['thumbnails']
                    track['artists'] = music_track['artistNames']
                    # in case the song is unavailable, there is no videoId
                    track['videoId'] = music_track['videoId'] if 'videoId' in item['payload'][
                        'musicTrack'] else None
                    # very occasionally lengthMs is not returned
                    track['lengthMs'] = music_track[
                        'lengthMs'] if 'lengthMs' in music_track else None
                    track['likeStatus'] = track_library_details[item['entityKey']]
                    track['isExplicit'] = music_track['contentRating'][
                        'explicitType'] == 'MUSIC_ENTITY_EXPLICIT_TYPE_EXPLICIT'
                    if 'libraryEdit' in music_track:
                        track['feedbackTokens'] = track_library_details[music_track['libraryEdit']]
                    album['tracks'].append(track)

        return album

    def get_song(self, videoId: str) -> Dict:
        """
        Returns metadata about a song or video.

        :param videoId: Video id
        :return: Dictionary with song metadata.

        Example::

            {
              "videoId": "ZrOKjDZOtkA",
              "title": "Wonderwall (Remastered)",
              "lengthSeconds": "259",
              "keywords": [
                "Oasis",
                "(What's",
                "..."
              ],
              "channelId": "UCmMUZbaYdNH0bEd1PAlAqsA",
              "isOwnerViewing": false,
              "shortDescription": "Provided to YouTube by Ignition...",
              "isCrawlable": true,
              "thumbnail": {
                "thumbnails": [
                  {
                    "url": "https://i.ytimg.com/vi/ZrOKjDZOtkA/maxresdefault.jpg",
                    "width": 1920,
                    "height": 1080
                  }
                ]
              },
              "averageRating": 4.5673099,
              "allowRatings": true,
              "viewCount": "18136380",
              "author": "Oasis - Topic",
              "isPrivate": false,
              "isUnpluggedCorpus": false,
              "isLiveContent": false,
              "provider": "Ignition",
              "artists": [
                "Oasis"
              ],
              "copyright": "℗ 2014 Big Brother Recordings ...",
              "production": [
                "Composer: Noel Gallagher",
                "Lyricist: Noel Gallagher",
                "Producer: Owen Morris & Noel Gallagher"
              ],
              "release": "2014-09-29"
              "category": "Music"
            }

        """
        endpoint = "https://www.youtube.com/get_video_info"
        params = {"video_id": videoId, "hl": self.language, "el": "detailpage"}
        response = requests.get(endpoint, params, headers=self.headers, proxies=self.proxies)
        text = parse_qs(response.text)
        if 'player_response' not in text:
            return text
        player_response = json.loads(text['player_response'][0])
        song_meta = player_response['videoDetails']
        song_meta['category'] = player_response['microformat']['playerMicroformatRenderer'][
            'category']
        if song_meta['shortDescription'].endswith("Auto-generated by YouTube."):
            try:
                description = song_meta['shortDescription'].split('\n\n')
                for i, detail in enumerate(description):
                    description[i] = codecs.escape_decode(detail)[0].decode('utf-8')
                song_meta['provider'] = description[0].replace('Provided to YouTube by ', '')
                song_meta['artists'] = [artist for artist in description[1].split(' · ')[1:]]
                song_meta['copyright'] = description[3]
                song_meta['release'] = None if len(description) < 5 else description[4].replace(
                    'Released on: ', '')
                song_meta['production'] = None if len(description) < 6 else [
                    pub for pub in description[5].split('\n')
                ]
            except (KeyError, IndexError):
                pass
        return song_meta

    def get_streaming_data(self, videoId: str) -> Dict:
        """
        Returns the streaming data for a song or video.

        :param videoId: Video id
        :return: Dictionary with song streaming data.

        Example::

            {
                "expiresInSeconds": "21540",
                "formats": [
                    {
                        "itag": 18,
                        "mimeType": "video/mp4; codecs=\"avc1.42001E, mp4a.40.2\"",
                        "bitrate": 306477,
                        "width": 360,
                        "height": 360,
                        "lastModified": "1574970034520502",
                        "contentLength": "9913027",
                        "quality": "medium",
                        "fps": 25,
                        "qualityLabel": "360p",
                        "projectionType": "RECTANGULAR",
                        "averageBitrate": 306419,
                        "audioQuality": "AUDIO_QUALITY_LOW",
                        "approxDurationMs": "258809",
                        "audioSampleRate": "44100",
                        "audioChannels": 2,
                        "signatureCipher": "s=..."
                    }
                ],
                "adaptiveFormats": [
                    {
                        "itag": 137,
                        "mimeType": "video/mp4; codecs=\"avc1.640020\"",
                        "bitrate": 312234,
                        "width": 1078,
                        "height": 1080,
                        "initRange": {
                            "start": "0",
                            "end": "738"
                        },
                        "indexRange": {
                            "start": "739",
                            "end": "1382"
                        },
                        "lastModified": "1574970033536914",
                        "contentLength": "5674377",
                        "quality": "hd1080",
                        "fps": 25,
                        "qualityLabel": "1080p",
                        "projectionType": "RECTANGULAR",
                        "averageBitrate": 175432,
                        "approxDurationMs": "258760",
                        "signatureCipher": "s=..."
                    },
                    {...},
                    {
                        "itag": 140,
                        "mimeType": "audio/mp4; codecs=\"mp4a.40.2\"",
                        "bitrate": 131205,
                        "initRange": {
                            "start": "0",
                            "end": "667"
                        },
                        "indexRange": {
                            "start": "668",
                            "end": "1011"
                        },
                        "lastModified": "1574969975805792",
                        "contentLength": "4189579",
                        "quality": "tiny",
                        "projectionType": "RECTANGULAR",
                        "averageBitrate": 129521,
                        "highReplication": true,
                        "audioQuality": "AUDIO_QUALITY_MEDIUM",
                        "approxDurationMs": "258773",
                        "audioSampleRate": "44100",
                        "audioChannels": 2,
                        "loudnessDb": 1.1422243,
                        "signatureCipher": "s=..."
                    },
                    {...}
                ]
            }

        """
        endpoint = "https://www.youtube.com/get_video_info"
        params = {
            "video_id": videoId,
            "hl": self.language,
            "el": "detailpage",
            "c": "WEB_REMIX",
            "cver": "0.1"
        }
        response = requests.get(endpoint, params, headers=self.headers, proxies=self.proxies)
        text = parse_qs(response.text)
        if 'player_response' not in text:
            return text

        player_response = json.loads(text['player_response'][0])
        if 'streamingData' not in player_response:
            raise Exception('This video is not playable.')

        return player_response['streamingData']

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
        if 'sectionListRenderer' in response['contents'].keys():
            lyrics['lyrics'] = response['contents']['sectionListRenderer']['contents'][0][
                'musicDescriptionShelfRenderer']['description']['runs'][0]['text']
            lyrics['source'] = response['contents']['sectionListRenderer']['contents'][0][
                'musicDescriptionShelfRenderer']['footer']['runs'][0]['text']

        return lyrics
