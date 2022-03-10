from typing import List, Dict, Union
from ytmusicapi.parsers.watch import *


class WatchMixin:
    def get_watch_playlist(self,
                           videoId: str = None,
                           playlistId: str = None,
                           limit=25,
                           params: str = None) -> Dict[str, Union[List[Dict]]]:
        """
        Get a watch list of tracks. This watch playlist appears when you press
        play on a track in YouTube Music.

        Please note that the `INDIFFERENT` likeStatus of tracks returned by this
        endpoint may be either `INDIFFERENT` or `DISLIKE`, due to ambiguous data
        returned by YouTube Music.

        :param videoId: videoId of the played video
        :param playlistId: playlistId of the played playlist or album
        :param limit: minimum number of watch playlist items to return
        :param params: only used internally by :py:func:`get_watch_playlist_shuffle`
        :return: List of watch playlist items. The counterpart key is optional and only
            appears if a song has a corresponding video counterpart (UI song/video
            switcher).

        Example::

            {
                "tracks": [
                    {
                      "videoId": "9mWr4c_ig54",
                      "title": "Foolish Of Me (feat. Jonathan Mendelsohn)",
                      "length": "3:07",
                      "thumbnail": [
                        {
                          "url": "https://lh3.googleusercontent.com/ulK2YaLtOW0PzcN7ufltG6e4ae3WZ9Bvg8CCwhe6LOccu1lCKxJy2r5AsYrsHeMBSLrGJCNpJqXgwczk=w60-h60-l90-rj",
                          "width": 60,
                          "height": 60
                        }...
                      ],
                      "feedbackTokens": {
                        "add": "AB9zfpIGg9XN4u2iJ...",
                        "remove": "AB9zfpJdzWLcdZtC..."
                      },
                      "likeStatus": "INDIFFERENT",
                      "artists": [
                        {
                          "name": "Seven Lions",
                          "id": "UCYd2yzYRx7b9FYnBSlbnknA"
                        },
                        {
                          "name": "Jason Ross",
                          "id": "UCVCD9Iwnqn2ipN9JIF6B-nA"
                        },
                        {
                          "name": "Crystal Skies",
                          "id": "UCTJZESxeZ0J_M7JXyFUVmvA"
                        }
                      ],
                      "album": {
                        "name": "Foolish Of Me",
                        "id": "MPREb_C8aRK1qmsDJ"
                      },
                      "year": "2020",
                      "counterpart": {
                        "videoId": "E0S4W34zFMA",
                        "title": "Foolish Of Me [ABGT404] (feat. Jonathan Mendelsohn)",
                        "length": "3:07",
                        "thumbnail": [...],
                        "feedbackTokens": null,
                        "likeStatus": "LIKE",
                        "artists": [
                          {
                            "name": "Jason Ross",
                            "id": null
                          },
                          {
                            "name": "Seven Lions",
                            "id": null
                          },
                          {
                            "name": "Crystal Skies",
                            "id": null
                          }
                        ],
                        "views": "6.6K"
                      }
                    },...
                ],
                "playlistId": "RDAMVM4y33h81phKU",
                "lyrics": "MPLYt_HNNclO0Ddoc-17"
            }

        """
        body = {'enablePersistentPlaylistPanel': True, 'isAudioOnly': True}
        if not videoId and not playlistId:
            raise Exception("You must provide either a video id, a playlist id, or both")
        if videoId:
            body['videoId'] = videoId
            if not playlistId:
                playlistId = "RDAMVM" + videoId
            if not params:
                body['watchEndpointMusicSupportedConfigs'] = {
                    'watchEndpointMusicConfig': {
                        'hasPersistentPlaylistPanel': True,
                        'musicVideoType': "MUSIC_VIDEO_TYPE_ATV",
                    }
                }
        body['playlistId'] = validate_playlist_id(playlistId)
        is_playlist = body['playlistId'].startswith('PL') or \
                      body['playlistId'].startswith('OLA')
        if params:
            body['params'] = params
        endpoint = 'next'
        response = self._send_request(endpoint, body)
        watchNextRenderer = nav(response, [
            'contents', 'singleColumnMusicWatchNextResultsRenderer', 'tabbedRenderer',
            'watchNextTabbedResultsRenderer'
        ])

        lyrics_browse_id = None
        if 'unselectable' not in watchNextRenderer['tabs'][1]['tabRenderer']:
            lyrics_browse_id = watchNextRenderer['tabs'][1]['tabRenderer']['endpoint'][
                'browseEndpoint']['browseId']

        results = nav(watchNextRenderer,
                      TAB_CONTENT + ['musicQueueRenderer', 'content', 'playlistPanelRenderer'])
        playlist = next(
            filter(
                bool,
                map(
                    lambda x: nav(x, ['playlistPanelVideoRenderer'] + NAVIGATION_PLAYLIST_ID, True
                                  ), results['contents'])), None)
        tracks = parse_watch_playlist(results['contents'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_watch_playlist(contents)
            tracks.extend(
                get_continuations(results, 'playlistPanelContinuation', limit - len(tracks),
                                  request_func, parse_func, '' if is_playlist else 'Radio'))

        return dict(tracks=tracks, playlistId=playlist, lyrics=lyrics_browse_id)

    def get_watch_playlist_shuffle(self,
                                   videoId: str = None,
                                   playlistId: str = None,
                                   limit=50) -> Dict[str, Union[List[Dict]]]:
        """
        Shuffle any playlist

        :param videoId: Optional video id of the first video in the shuffled playlist
        :param playlistId: Playlist id
        :param limit: The number of watch playlist items to return
        :return: A list of watch playlist items (see :py:func:`get_watch_playlist`)
        """
        return self.get_watch_playlist(videoId=videoId,
                                       playlistId=playlistId,
                                       limit=limit,
                                       params='wAEB8gECKAE%3D')
