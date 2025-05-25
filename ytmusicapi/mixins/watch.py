from ytmusicapi.continuations import get_continuations
from ytmusicapi.exceptions import YTMusicServerError, YTMusicUserError
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.playlists import validate_playlist_id
from ytmusicapi.parsers.watch import *
from ytmusicapi.type_alias import JsonList, ParseFuncType, RequestFuncType


class WatchMixin(MixinProtocol):
    def get_watch_playlist(
        self,
        videoId: str | None = None,
        playlistId: str | None = None,
        limit: int = 25,
        radio: bool = False,
        shuffle: bool = False,
    ) -> dict[str, JsonList | str | None]:
        """
        Get a watch list of tracks. This watch playlist appears when you press
        play on a track in YouTube Music.

        Please note that the ``INDIFFERENT`` likeStatus of tracks returned by this
        endpoint may be either ``INDIFFERENT`` or ``DISLIKE``, due to ambiguous data
        returned by YouTube Music.

        :param videoId: videoId of the played video
        :param playlistId: playlistId of the played playlist or album
        :param limit: minimum number of watch playlist items to return
        :param radio: get a radio playlist (changes each time)
        :param shuffle: shuffle the input playlist. only works when the playlistId parameter
            is set at the same time. does not work if radio=True
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
                      "videoType": "MUSIC_VIDEO_TYPE_ATV",
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
        body = {
            "enablePersistentPlaylistPanel": True,
            "isAudioOnly": True,
            "tunerSettingValue": "AUTOMIX_SETTING_NORMAL",
        }
        if not videoId and not playlistId:
            raise YTMusicUserError("You must provide either a video id, a playlist id, or both")
        if videoId:
            body["videoId"] = videoId
            if not playlistId:
                playlistId = "RDAMVM" + videoId
            if not (radio or shuffle):
                body["watchEndpointMusicSupportedConfigs"] = {
                    "watchEndpointMusicConfig": {
                        "hasPersistentPlaylistPanel": True,
                        "musicVideoType": "MUSIC_VIDEO_TYPE_ATV",
                    }
                }
        is_playlist = False
        if playlistId:
            playlist_id = validate_playlist_id(playlistId)
            is_playlist = playlist_id.startswith("PL") or playlist_id.startswith("OLA")
            body["playlistId"] = playlist_id

        if shuffle and playlistId is not None:
            body["params"] = "wAEB8gECKAE%3D"
        if radio:
            body["params"] = "wAEB"
        endpoint = "next"
        response = self._send_request(endpoint, body)
        watchNextRenderer = nav(
            response,
            [
                "contents",
                "singleColumnMusicWatchNextResultsRenderer",
                "tabbedRenderer",
                "watchNextTabbedResultsRenderer",
            ],
        )

        lyrics_browse_id = get_tab_browse_id(watchNextRenderer, 1)
        related_browse_id = get_tab_browse_id(watchNextRenderer, 2)

        results = nav(
            watchNextRenderer, [*TAB_CONTENT, "musicQueueRenderer", "content", "playlistPanelRenderer"], True
        )
        if not results:
            msg = "No content returned by the server."
            if playlistId:
                msg += f"\nEnsure you have access to {playlistId} - a private playlist may cause this."
            raise YTMusicServerError(msg)

        playlist = next(
            filter(
                bool,
                map(
                    lambda x: nav(x, ["playlistPanelVideoRenderer", *NAVIGATION_PLAYLIST_ID], True),
                    results["contents"],
                ),
            ),
            None,
        )
        tracks = parse_watch_playlist(results["contents"])

        if "continuations" in results:
            request_func: RequestFuncType = lambda additionalParams: self._send_request(
                endpoint, body, additionalParams
            )
            parse_func: ParseFuncType = lambda contents: parse_watch_playlist(contents)
            tracks.extend(
                get_continuations(
                    results,
                    "playlistPanelContinuation",
                    limit - len(tracks),
                    request_func,
                    parse_func,
                    "" if is_playlist else "Radio",
                )
            )

        return dict(tracks=tracks, playlistId=playlist, lyrics=lyrics_browse_id, related=related_browse_id)
