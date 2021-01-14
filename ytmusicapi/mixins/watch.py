from typing import List, Dict
from ytmusicapi.parsers.watch import *


class WatchMixin:
    def get_watch_playlist(self,
                           videoId: str = None,
                           playlistId: str = None,
                           limit=25,
                           params: str = None) -> Dict[List[Dict], str]:
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
        :return: List of watch playlist items.

        Example::

            {
                "tracks": [
                    {
                      "title": "Interstellar (Main Theme) - Piano Version",
                      "byline": "Patrik Pietschmann • 47M views",
                      "length": "4:47",
                      "videoId": "4y33h81phKU",
                      "playlistId": "RDAMVM4y33h81phKU",
                      "thumbnail": [
                        {
                          "url": "https://i.ytimg.com/vi/4y...",
                          "width": 400,
                          "height": 225
                        }
                      ],
                      "feedbackTokens": [],
                      "likeStatus": "LIKE"
                    },...
                ],
                "lyrics": "MPLYt_HNNclO0Ddoc-17"
            }

        """
        body = {'enablePersistentPlaylistPanel': True, 'isAudioOnly': True}
        if videoId:
            body['videoId'] = videoId
            body['watchEndpointMusicSupportedConfigs'] = {
                'watchEndpointMusicConfig': {
                    'hasPersistentPlaylistPanel': True,
                    'musicVideoType': "MUSIC_VIDEO_TYPE_OMV",
                }
            }
        is_playlist = False
        if playlistId:
            body['playlistId'] = playlistId
            is_playlist = playlistId.startswith('PL')
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
        tracks = parse_watch_playlist(results['contents'])

        if 'continuations' in results:
            request_func = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams)
            parse_func = lambda contents: parse_watch_playlist(contents)
            tracks.extend(
                get_continuations(results, 'playlistPanelContinuation', limit - len(tracks),
                                  request_func, parse_func, '' if is_playlist else 'Radio'))

        return {'tracks': tracks, 'lyrics': lyrics_browse_id}

    def get_watch_playlist_shuffle(self,
                                   playlistId: str = None,
                                   limit=50) -> Dict[List[Dict], str]:
        """
        Shuffle any playlist

        :param playlistId: Playlist id
        :param limit: The number of watch playlist items to return
        :return: A list of watch playlist items (see :py:func:`get_watch_playlist`)
        """
        return self.get_watch_playlist(playlistId=playlistId, limit=limit, params='wAEB8gECGAE%3D')
