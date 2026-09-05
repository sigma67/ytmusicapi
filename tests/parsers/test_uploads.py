from ytmusicapi.continuations import get_continuations
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.models.uploads import UploadAlbum, UploadSong
from ytmusicapi.parsers.uploads import parse_upload_album, parse_uploaded_items

ARTIST_ID = "FEmusic_library_privately_owned_artist_detaila_po_CICr2crg7OWpchIIY29sZHBsYXk"
ALBUM_ID = "FEmusic_library_privately_owned_release_detailb_po_55chars"


def _menu(video_id: str, entity_id: str, like_status: str = "LIKE") -> dict:
    delete_command = {
        "confirmDialogEndpoint": {
            "content": {
                "confirmDialogRenderer": {
                    "confirmButton": {
                        "buttonRenderer": {
                            "command": {"musicDeletePrivatelyOwnedEntityCommand": {"entityId": entity_id}}
                        }
                    }
                }
            }
        }
    }
    return {
        "menuRenderer": {
            "items": [
                {
                    "menuServiceItemRenderer": {
                        "serviceEndpoint": {"queueAddEndpoint": {"queueTarget": {"videoId": video_id}}}
                    }
                },
                {"menuNavigationItemRenderer": {"navigationEndpoint": delete_command}},
            ],
            "topLevelButtons": [{"likeButtonRenderer": {"likeStatus": like_status}}],
        }
    }


def _flex_column(run: dict) -> dict:
    return {"musicResponsiveListItemFlexColumnRenderer": {"text": {"runs": [run]}}}


def _linked_run(text: str, browse_id: str) -> dict:
    return {"text": text, "navigationEndpoint": {"browseEndpoint": {"browseId": browse_id}}}


def _upload_song_item(like_status: str = "LIKE") -> dict:
    return {
        "musicResponsiveListItemRenderer": {
            "menu": _menu("Uise6RPKoek", "t_po_CICr2crg7OWpchDpjPjrBA", like_status),
            "flexColumns": [
                _flex_column({"text": "A Sky Full Of Stars"}),
                _flex_column(_linked_run("Coldplay", ARTIST_ID)),
                _flex_column(_linked_run("Ghost Stories", ALBUM_ID)),
            ],
            "fixedColumns": [
                {"musicResponsiveListItemFixedColumnRenderer": {"text": {"runs": [{"text": "4:15"}]}}}
            ],
            "thumbnail": {
                "musicThumbnailRenderer": {
                    "thumbnail": {
                        "thumbnails": [
                            {"url": "https://i.ytimg.com/vi/Uise6RPKoek/s.jpg", "width": 60, "height": 60}
                        ]
                    }
                }
            },
        }
    }


class TestParseUploadedItems:
    def test_parses_uploaded_song(self):
        song = parse_uploaded_items([_upload_song_item()])[0]

        assert isinstance(song, UploadSong)
        assert song["entityId"] == "t_po_CICr2crg7OWpchDpjPjrBA"
        assert song.videoId == "Uise6RPKoek"
        assert song.title == "A Sky Full Of Stars"
        assert song.duration == "4:15"
        assert song.duration_seconds == 255
        assert song.artists[0].name == "Coldplay"
        assert song.artists[0].id == ARTIST_ID
        assert song.album.name == "Ghost Stories"
        assert song.album.id == ALBUM_ID
        assert song.likeStatus == "LIKE"
        assert song.thumbnails[0].url == "https://i.ytimg.com/vi/Uise6RPKoek/s.jpg"

    # missing data stays a present key with None value, per the #307 semantics
    def test_missing_fields_are_present_with_none(self):
        item = _upload_song_item()
        del item["musicResponsiveListItemRenderer"]["fixedColumns"]
        del item["musicResponsiveListItemRenderer"]["flexColumns"][2]
        del item["musicResponsiveListItemRenderer"]["thumbnail"]

        song = parse_uploaded_items([item])[0]

        assert song.duration is None
        assert song.duration_seconds is None
        assert song.album is None
        assert song.thumbnails is None
        assert {"duration", "duration_seconds", "album", "thumbnails"} <= set(song)

    def test_unknown_like_status_maps_to_indifferent(self):
        song = parse_uploaded_items([_upload_song_item(like_status="SOMETHING_ELSE")])[0]

        assert song.likeStatus is LikeStatus.INDIFFERENT

    def test_item_without_menu_is_skipped(self):
        item = _upload_song_item()
        del item["musicResponsiveListItemRenderer"]["menu"]

        assert parse_uploaded_items([item]) == []

    def test_dict_access_matches_attribute_access(self):
        song = parse_uploaded_items([_upload_song_item()])[0]

        assert song["title"] == song.title
        assert song.get("entityId") == song.entityId


def test_continuations_with_model_parse_func():
    shelf = {
        "contents": [_upload_song_item()],
        "continuations": [{"nextContinuationData": {"continuation": "ctoken1"}}],
    }
    continuation_response = {
        "continuationContents": {
            "musicShelfContinuation": {"contents": [_upload_song_item(like_status="INDIFFERENT")]}
        }
    }

    def request_func(additional_params: str) -> dict:
        assert "ctoken1" in additional_params
        return continuation_response

    # the caller parses the first page itself; get_continuations returns only
    # the continuation pages, composed the same way the mixin composes them
    songs = parse_uploaded_items(shelf["contents"])
    songs.extend(get_continuations(shelf, "musicShelfContinuation", 100, request_func, parse_uploaded_items))

    assert len(songs) == 2
    assert all(isinstance(song, UploadSong) for song in songs)
    assert songs[0].likeStatus == LikeStatus.LIKE
    assert songs[1].likeStatus == LikeStatus.INDIFFERENT


def _album_response(track_items: list[dict]) -> dict:
    header = {
        "musicDetailHeaderRenderer": {
            "title": {"runs": [{"text": "18 Months"}]},
            "subtitle": {
                "runs": [
                    {"text": "Album"},
                    {"text": " • "},
                    _linked_run("Calvin Harris", ARTIST_ID),
                    {"text": " • "},
                    {"text": "2012"},
                ]
            },
            "secondSubtitle": {"runs": [{"text": "2"}, {"text": " songs"}, {"text": "8 minutes"}]},
            "menu": {
                "menuRenderer": {
                    "topLevelButtons": [
                        {
                            "buttonRenderer": {
                                "navigationEndpoint": {
                                    "watchPlaylistEndpoint": {"playlistId": "MLPRb_po_55chars"}
                                }
                            }
                        }
                    ]
                }
            },
        }
    }
    shelf = {"sectionListRenderer": {"contents": [{"musicShelfRenderer": {"contents": track_items}}]}}
    return {
        "header": header,
        "contents": {"singleColumnBrowseResultsRenderer": {"tabs": [{"tabRenderer": {"content": shelf}}]}},
    }


class TestParseUploadAlbum:
    def test_parses_album_with_tracks(self):
        album = parse_upload_album(_album_response([_upload_song_item()]))

        assert isinstance(album, UploadAlbum)
        assert album.title == "18 Months"
        assert album.type == "Album"
        assert album.artists[0].name == "Calvin Harris"
        assert album.year == "2012"
        assert album.trackCount == 2
        assert album.duration == "8 minutes"
        assert album.audioPlaylistId == "MLPRb_po_55chars"
        assert album.description is None
        assert album.likeStatus is None
        assert isinstance(album.tracks[0], UploadSong)
        assert album["tracks"][0]["entityId"] == "t_po_CICr2crg7OWpchDpjPjrBA"
        # one 4:15 track => 255 seconds total
        assert album.duration_seconds == 255

    def test_duration_seconds_sums_all_tracks(self):
        album = parse_upload_album(_album_response([_upload_song_item(), _upload_song_item()]))

        assert album.duration_seconds == 510
