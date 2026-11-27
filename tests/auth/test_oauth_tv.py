"""Offline tests for the TV client code path used with OAuth authentication, see #813"""

import base64
import json
import time
from unittest import mock

import pytest
from requests import Response

from ytmusicapi import OAuthCredentials, YTMusic
from ytmusicapi.auth.types import AuthType
from ytmusicapi.constants import TV_CLIENT_NAME, TV_UNSUPPORTED, TV_USER_AGENT, YT_DATA_API
from ytmusicapi.exceptions import YTMusicServerError, YTMusicUserError
from ytmusicapi.type_alias import JsonDict


def text(value: str) -> dict:
    return {"simpleText": value}


def lines(*rows: list[dict]) -> list[dict]:
    return [
        {"lineRenderer": {"items": [{"lineItemRenderer": {"text": item}} for item in row]}} for row in rows
    ]


def playlist_tile(browse_id: str, title: str, *rows: list[dict]) -> dict:
    return {
        "tileRenderer": {
            "header": {
                "tileHeaderRenderer": {"thumbnail": {"thumbnails": [{"url": "u", "width": 1, "height": 1}]}}
            },
            "metadata": {
                "tileMetadataRenderer": {"title": {"runs": [{"text": title}]}, "lines": lines(*rows)}
            },
            "onSelectCommand": {"browseEndpoint": {"browseId": browse_id}},
            "contentType": "TILE_CONTENT_TYPE_PLAYLIST",
        }
    }


def track_tile(video_id: str, title: str, set_video_id: str | None = None) -> dict:
    tile: dict = {
        "header": {
            "tileHeaderRenderer": {
                "thumbnail": {"thumbnails": []},
                "thumbnailOverlays": [{"thumbnailOverlayTimeStatusRenderer": {"text": text("4:40")}}],
            }
        },
        "metadata": {
            "tileMetadataRenderer": {
                "title": text(title),
                "lines": lines(
                    [
                        {
                            "runs": [
                                {
                                    "text": "Oasis",
                                    "navigationEndpoint": {"browseEndpoint": {"browseId": "UCartist"}},
                                }
                            ]
                        }
                    ],
                    [text("720M views"), text("•"), text("18 years ago")],
                ),
            }
        },
        "onSelectCommand": {"watchEndpoint": {"videoId": video_id}},
        "contentId": video_id,
    }
    if set_video_id:
        tile["onLongPressCommand"] = {
            "showMenuCommand": {
                "menu": {
                    "menuRenderer": {
                        "items": [
                            {"menuNavigationItemRenderer": {"text": {"runs": [{"text": "Play"}]}}},
                            {
                                "menuServiceItemRenderer": {
                                    "serviceEndpoint": {
                                        "playlistEditEndpoint": {
                                            "actions": [
                                                {"setVideoId": set_video_id, "action": "ACTION_REMOVE_VIDEO"}
                                            ]
                                        }
                                    }
                                }
                            },
                        ]
                    }
                }
            }
        }
    return {"tileRenderer": tile}


def lockup(content_type: str, content_id: str, title: str, *rows: list[str]) -> dict:
    return {
        "lockupViewModel": {
            "contentImage": {
                "thumbnailViewModel": {
                    "image": {"sources": [{"url": "u"}]},
                    "overlays": [
                        {
                            "thumbnailBottomOverlayViewModel": {
                                "badges": [{"thumbnailBadgeViewModel": {"text": "4:40"}}]
                            }
                        }
                    ],
                }
            },
            "metadata": {
                "lockupMetadataViewModel": {
                    "title": {"content": title},
                    "metadata": {
                        "contentMetadataViewModel": {
                            "metadataRows": [
                                {"metadataParts": [{"text": {"content": part}} for part in row]}
                                for row in rows
                            ]
                        }
                    },
                }
            },
            "contentId": content_id,
            "contentType": "LOCKUP_CONTENT_TYPE_" + content_type,
        }
    }


LIBRARY_RESPONSE = {
    "contents": {
        "tvBrowseRenderer": {
            "content": {
                "tvSecondaryNavRenderer": {
                    "sections": [
                        {
                            "tvSecondaryNavSectionRenderer": {
                                "tabs": [
                                    {"tabRenderer": {"title": "Recent activity", "selected": False}},
                                    {
                                        "tabRenderer": {
                                            "title": "Playlists",
                                            "selected": True,
                                            "content": {
                                                "tvSurfaceContentRenderer": {
                                                    "content": {
                                                        "gridRenderer": {
                                                            "items": [
                                                                playlist_tile(
                                                                    "VLLM",
                                                                    "Liked Music",
                                                                    [
                                                                        text(
                                                                            "Auto playlist • me • 1,450 songs"
                                                                        )
                                                                    ],
                                                                ),
                                                                playlist_tile(
                                                                    "VLPLown",
                                                                    "Mine",
                                                                    [text("me")],
                                                                    [text("Playlist • 35 tracks")],
                                                                ),
                                                            ]
                                                        }
                                                    }
                                                }
                                            },
                                        }
                                    },
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
}

PLAYLIST_RESPONSE = {
    "contents": {
        "tvBrowseRenderer": {
            "content": {
                "tvSurfaceContentRenderer": {
                    "content": {
                        "twoColumnRenderer": {
                            "leftColumn": {
                                "entityMetadataRenderer": {
                                    "title": text("Mine"),
                                    "description": {},
                                    "bylines": [
                                        {
                                            "lineRenderer": {
                                                "items": [
                                                    {
                                                        "lineItemRenderer": {
                                                            "badge": {
                                                                "metadataBadgeRenderer": {
                                                                    "icon": {"iconType": "PRIVACY_PRIVATE"}
                                                                }
                                                            }
                                                        }
                                                    },
                                                    {"lineItemRenderer": {"text": text("me")}},
                                                    {"lineItemRenderer": {"text": text("•")}},
                                                    {
                                                        "lineItemRenderer": {
                                                            "text": {
                                                                "runs": [{"text": "3"}, {"text": " videos"}]
                                                            }
                                                        }
                                                    },
                                                    {"lineItemRenderer": {"text": text("•")}},
                                                    {"lineItemRenderer": {"text": text("No views")}},
                                                ]
                                            }
                                        }
                                    ],
                                }
                            },
                            "rightColumn": {
                                "playlistVideoListRenderer": {
                                    "contents": [track_tile("vid1", "Wonderwall", "SET1")],
                                    "playlistId": "PLown",
                                    "isEditable": True,
                                    "continuations": [{"nextContinuationData": {"continuation": "TOKEN"}}],
                                }
                            },
                        }
                    }
                }
            }
        }
    }
}

PLAYLIST_CONTINUATION = {
    "continuationContents": {
        "playlistVideoListContinuation": {
            "contents": [track_tile("vid2", "Whatever", "SET2")],
            "playlistId": "PLown",
        }
    }
}

SEARCH_RESPONSE = {
    "contents": {
        "sectionListRenderer": {
            "contents": [
                {
                    "shelfRenderer": {
                        "headerRenderer": {
                            "shelfHeaderRenderer": {
                                "avatarLockup": {"avatarLockupRenderer": {"title": text("Search results")}}
                            }
                        },
                        "content": {
                            "horizontalListRenderer": {
                                "items": [
                                    lockup(
                                        "MUSIC",
                                        "vid1",
                                        "Wonderwall",
                                        ["Oasis"],
                                        ["720M views", "18 years ago"],
                                    ),
                                    lockup("PLAYLIST", "PLother", "Best of", ["Someone"]),
                                    lockup("PLAYLIST", "OLAK5uy_album", "Morning Glory", ["Oasis"]),
                                    lockup("CHANNEL", "UCartist", "Oasis", ["@oasis"], ["5M subscribers"]),
                                    lockup("SHORT", "short1", "a short"),
                                ]
                            }
                        },
                    }
                }
            ]
        }
    }
}


def library_tab(*items: dict) -> dict:
    tab = {"title": "Tab", "selected": True}
    tab["content"] = {"tvSurfaceContentRenderer": {"content": {"gridRenderer": {"items": list(items)}}}}
    sections = [{"tvSecondaryNavSectionRenderer": {"tabs": [{"tabRenderer": tab}]}}]
    return {"contents": {"tvBrowseRenderer": {"content": {"tvSecondaryNavRenderer": {"sections": sections}}}}}


def typed(tile: dict, content_type: str, **extra: object) -> dict:
    tile["tileRenderer"].update({"contentType": "TILE_CONTENT_TYPE_" + content_type, **extra})
    return tile


def shelf(title: str, *items: dict, continuations: list[dict] | None = None) -> dict:
    content: dict = {"items": list(items)}
    if continuations is not None:
        content["continuations"] = continuations
    return {
        "shelfRenderer": {
            "headerRenderer": {"shelfHeaderRenderer": {"title": text(title)}},
            "content": {"horizontalListRenderer": content},
        }
    }


ALBUM_TILE = playlist_tile("VLOLAK5uy_album", "Morning Glory", [text("Oasis")], [text("Album • 1995")])
CHANNEL_TILE = typed(
    {
        "tileRenderer": {
            "metadata": {"tileMetadataRenderer": {"title": text("Oasis"), "lines": lines([text("Mix")])}},
            "onSelectCommand": {"watchPlaylistEndpoint": {"playlistId": "RDEMradio"}},
            "contentId": "RDEMradio",
        }
    },
    "CHANNEL",
)
ALBUM_TRACK_TILE = typed(
    {
        "tileRenderer": {
            "header": {"trackTileHeaderRenderer": {"title": text("Hello"), "duration": text("3:21")}},
            "onSelectCommand": {"watchEndpoint": {"videoId": "vid9"}},
        }
    },
    "VIDEO",
)

ARTIST_RESPONSE = {
    "contents": {
        "tvBrowseRenderer": {
            "content": {
                "tvSurfaceContentRenderer": {
                    "header": {
                        "channelHeaderRenderer": {
                            "title": text("Oasis"),
                            "subtitle": lines([text("@oasis"), text("•"), text("5M subscribers")])[0],
                            "buttons": [
                                {
                                    "buttonRenderer": {
                                        "icon": {"iconType": "MIX"},
                                        "navigationEndpoint": {
                                            "watchPlaylistEndpoint": {"playlistId": "RDEMradio"}
                                        },
                                    }
                                },
                                {"subscribeButtonRenderer": {"channelId": "UCartist", "subscribed": True}},
                            ],
                        }
                    },
                    "content": {
                        "sectionListRenderer": {
                            "contents": [
                                shelf("Videos", typed(track_tile("vid1", "Wonderwall"), "VIDEO")),
                                shelf("Albums", ALBUM_TILE),
                                shelf("Shorts", typed(track_tile("short1", "a short"), "SHORTS")),
                            ]
                        }
                    },
                }
            }
        }
    }
}


def queue_item(video_id: str, title: str) -> dict:
    return {"playlistPanelVideoWrapperRenderer": {"primaryRenderer": track_tile(video_id, title)}}


WATCH_RESPONSE = {
    "contents": {
        "singleColumnWatchNextResults": {
            "playlist": {"playlist": {"playlistId": "RDAMVMvid1"}},
            "pivot": {
                "sectionListRenderer": {
                    "contents": [
                        shelf(
                            "Up next",
                            queue_item("vid1", "Wonderwall"),
                            continuations=[
                                {"reloadContinuationData": {"continuation": "RELOAD"}},
                                {"nextRadioContinuationData": {"continuation": "NEXT"}},
                            ],
                        ),
                        shelf("Recommended", typed(track_tile("other", "Other"), "VIDEO")),
                    ]
                }
            },
        }
    }
}

WATCH_CONTINUATION = {
    "continuationContents": {
        "horizontalListContinuation": {
            "items": [queue_item("vid2", "Whatever")],
            "continuations": [{"previousContinuationData": {"continuation": "PREVIOUS"}}],
        }
    }
}


@pytest.fixture(name="yt_tv")
def fixture_yt_tv() -> YTMusic:
    token = {
        "scope": "https://www.googleapis.com/auth/youtube",
        "token_type": "Bearer",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_at": int(time.time()) + 3600,
        "expires_in": 3600,
    }
    yt = YTMusic(token, oauth_credentials=mock.Mock(spec=OAuthCredentials))
    # avoid the visitor id request
    with mock.patch("ytmusicapi.ytmusic.get_visitor_id", return_value={"X-Goog-Visitor-Id": "visitor"}):
        assert yt.base_headers
    return yt


class TestOAuthTVClient:
    def test_client_context(self, yt_tv: YTMusic):
        assert yt_tv.auth_type == AuthType.OAUTH_CUSTOM_CLIENT
        assert yt_tv.uses_tv_client
        assert yt_tv.context["context"]["client"]["clientName"] == TV_CLIENT_NAME
        assert yt_tv.headers["user-agent"] == TV_USER_AGENT
        assert yt_tv.headers["authorization"] == "Bearer test_access_token"
        assert not YTMusic().uses_tv_client

    def test_unsupported_request_hint(self, yt_tv: YTMusic):
        response = Response()
        response.status_code = 400
        response.reason = "Bad Request"
        response._content = json.dumps(
            {"error": {"message": "Request contains an invalid argument."}}
        ).encode()
        with (
            mock.patch.object(yt_tv._session, "post", return_value=response),
            pytest.raises(YTMusicServerError, match="not supported with OAuth"),
        ):
            yt_tv.get_library_playlists()

    def test_unsupported_functions(self, yt_tv: YTMusic):
        yt = YTMusic()
        for name in TV_UNSUPPORTED:
            assert callable(getattr(yt, name)), name
        with pytest.raises(YTMusicUserError, match="get_home is not supported with OAuth"):
            yt_tv.get_home()
        with pytest.raises(YTMusicUserError, match="get_album is not supported with OAuth"):
            yt_tv.get_album("MPREb_4pL8gzRtw1p")
        # other instances are not affected
        assert yt.get_home.__func__ is YTMusic.get_home

    def test_get_library_playlists(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=LIBRARY_RESPONSE):
            playlists = yt_tv.get_library_playlists()
        assert [p["playlistId"] for p in playlists] == ["LM", "PLown"]
        assert playlists[0]["count"] == 1450
        assert playlists[1] == {
            "title": "Mine",
            "playlistId": "PLown",
            "thumbnails": [{"url": "u", "width": 1, "height": 1}],
            "description": "me • Playlist • 35 tracks",
            "count": 35,
            "author": [{"name": "me", "id": None}],
        }

    def test_get_playlist(self, yt_tv: YTMusic):
        # the TV client is the fallback for playlists the Data API does not return
        with (
            mock.patch.object(yt_tv, "_send_data_api_request", side_effect=YTMusicServerError("404")),
            mock.patch.object(
                yt_tv, "_send_request", side_effect=[PLAYLIST_RESPONSE, PLAYLIST_CONTINUATION]
            ) as send,
        ):
            playlist = yt_tv.get_playlist("PLown", limit=None)
        assert send.call_args_list[0].args[1] == {"browseId": "VLPLown"}
        assert "TOKEN" in send.call_args_list[1].args[2]
        assert playlist["id"] == "PLown"
        assert playlist["owned"]
        assert playlist["privacy"] == "PRIVATE"
        assert playlist["title"] == "Mine"
        assert playlist["author"] == {"name": "me", "id": None}
        assert playlist["trackCount"] == 3
        assert playlist["duration_seconds"] == 560
        assert [(t["videoId"], t["setVideoId"]) for t in playlist["tracks"]] == [
            ("vid1", "SET1"),
            ("vid2", "SET2"),
        ]
        track = playlist["tracks"][0]
        assert track["title"] == "Wonderwall"
        assert track["artists"] == [{"name": "Oasis", "id": "UCartist"}]
        assert track["duration"] == "4:40"
        assert track["duration_seconds"] == 280

    def test_search(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=SEARCH_RESPONSE):
            results = yt_tv.search("Oasis Wonderwall")
            albums = yt_tv.search("Oasis Wonderwall", filter="albums")
        assert [r["resultType"] for r in results] == ["song", "playlist", "album", "artist"]
        assert results[0] == {
            "category": "Search results",
            "resultType": "song",
            "title": "Wonderwall",
            "thumbnails": [{"url": "u"}],
            "videoId": "vid1",
            "artists": [{"name": "Oasis", "id": None}],
            "views": "720M",
            "duration": "4:40",
            "duration_seconds": 280,
        }
        assert results[1]["playlistId"] == "PLother"
        assert results[3]["browseId"] == "UCartist"
        assert [r["playlistId"] for r in albums] == ["OLAK5uy_album"]

    def test_search_unsupported_filter(self, yt_tv: YTMusic):
        with pytest.raises(YTMusicUserError, match="OAuth"):
            yt_tv.search("Oasis", filter="podcasts")
        with pytest.raises(YTMusicUserError, match="OAuth"):
            yt_tv.search("Oasis", scope="library")

    def test_create_and_delete_playlist_use_data_api(self, yt_tv: YTMusic):
        created = Response()
        created.status_code = 200
        created._content = json.dumps({"id": "PLnew"}).encode()
        deleted = Response()
        deleted.status_code = 204
        deleted._content = b""
        with (
            mock.patch.object(yt_tv._session, "request", side_effect=[created, deleted]) as request,
            mock.patch.object(yt_tv, "_send_request", return_value={"status": "STATUS_SUCCEEDED"}) as send,
        ):
            assert yt_tv.create_playlist("title", "<b>desc</b>", "UNLISTED", video_ids=["vid1"]) == "PLnew"
            assert yt_tv.delete_playlist("PLnew") == "STATUS_SUCCEEDED"

        create_call, delete_call = request.call_args_list
        assert create_call.args[:2] == ("POST", YT_DATA_API + "playlists")
        assert create_call.kwargs["json"] == {
            "snippet": {"title": "title", "description": "desc"},
            "status": {"privacyStatus": "unlisted"},
        }
        assert create_call.kwargs["headers"] == {"authorization": "Bearer test_access_token"}
        assert delete_call.args[:2] == ("DELETE", YT_DATA_API + "playlists")
        assert delete_call.kwargs["params"] == {"id": "PLnew"}
        # videos are added with the regular playlist edit endpoint
        assert send.call_args.args[0] == "browse/edit_playlist"
        assert send.call_args.args[1]["playlistId"] == "PLnew"

    def test_get_library_albums_songs_subscriptions(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=library_tab(ALBUM_TILE)):
            assert yt_tv.get_library_albums() == [
                {
                    "browseId": None,
                    "playlistId": "OLAK5uy_album",
                    "title": "Morning Glory",
                    "type": "Album",
                    "year": "1995",
                    "artists": [{"name": "Oasis", "id": None}],
                    "thumbnails": [{"url": "u", "width": 1, "height": 1}],
                }
            ]
        songs = [typed(track_tile(f"vid{i}", "Song"), "VIDEO") for i in range(3)]
        with mock.patch.object(yt_tv, "_send_request", return_value=library_tab(*songs)):
            assert [song["videoId"] for song in yt_tv.get_library_songs(limit=2)] == ["vid0", "vid1"]
        with mock.patch.object(yt_tv, "_send_request", return_value=library_tab(CHANNEL_TILE)):
            assert yt_tv.get_library_subscriptions() == [
                {"artist": "Oasis", "browseId": None, "radioId": "RDEMradio", "thumbnails": None}
            ]

    def test_get_playlist_album_tracks(self, yt_tv: YTMusic):
        response = json.loads(json.dumps(PLAYLIST_RESPONSE))
        columns = response["contents"]["tvBrowseRenderer"]["content"]["tvSurfaceContentRenderer"]["content"]
        columns["twoColumnRenderer"]["rightColumn"]["playlistVideoListRenderer"] = {
            "contents": [ALBUM_TRACK_TILE],
            "playlistId": "OLAK5uy_album",
        }
        with (
            mock.patch.object(yt_tv, "_send_data_api_request", side_effect=YTMusicServerError("404")),
            mock.patch.object(yt_tv, "_send_request", return_value=response),
        ):
            playlist = yt_tv.get_playlist("OLAK5uy_album")
        assert not playlist["owned"]
        assert playlist["tracks"][0]["videoId"] == "vid9"
        assert playlist["tracks"][0]["title"] == "Hello"
        assert playlist["tracks"][0]["duration_seconds"] == 201

    def test_get_artist(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=ARTIST_RESPONSE):
            artist = yt_tv.get_artist("UCartist")
        assert artist["name"] == "Oasis"
        assert artist["channelId"] == "UCartist"
        assert artist["subscribers"] == "5M"
        assert artist["subscribed"] is True
        assert artist["radioId"] == "RDEMradio"
        assert [section["title"] for section in artist["sections"]] == ["Videos", "Albums"]
        assert artist["sections"][0]["contents"][0]["videoId"] == "vid1"
        assert artist["sections"][1]["contents"][0]["playlistId"] == "OLAK5uy_album"

    def test_get_watch_playlist(self, yt_tv: YTMusic):
        with mock.patch.object(
            yt_tv, "_send_request", side_effect=[WATCH_RESPONSE, WATCH_CONTINUATION]
        ) as send:
            watch = yt_tv.get_watch_playlist("vid1", limit=10)
        assert "NEXT" in send.call_args_list[1].args[2]
        assert watch["playlistId"] == "RDAMVMvid1"
        assert [track["videoId"] for track in watch["tracks"]] == ["vid1", "vid2"]
        assert watch["tracks"][0]["length"] == "4:40"
        assert watch["tracks"][0]["artists"] == [{"name": "Oasis", "id": "UCartist"}]

    def test_get_playlist_description(self, yt_tv: YTMusic):
        response = json.loads(json.dumps(PLAYLIST_RESPONSE))
        columns = response["contents"]["tvBrowseRenderer"]["content"]["tvSurfaceContentRenderer"]["content"]
        popup: dict = {"subtitle": text("my description")}
        for key in (
            "overlayMessageRenderer",
            "items",
            "scrollPaneItemListRenderer",
            "content",
            "scrollPaneRenderer",
            "content",
            "overlayPanelRenderer",
            "actionPanel",
            "overlayTwoPanelRenderer",
            "overlay",
            "overlaySectionRenderer",
            "popup",
            "openPopupAction",
            "command",
            "buttonRenderer",
        ):
            popup = {key: [popup] if key == "items" else popup}
        columns["twoColumnRenderer"]["leftColumn"]["entityMetadataRenderer"]["buttons"] = [
            {"buttonRenderer": {"text": text("Play")}},
            popup,
        ]
        with (
            mock.patch.object(yt_tv, "_send_data_api_request", side_effect=YTMusicServerError("404")),
            mock.patch.object(yt_tv, "_send_request", side_effect=[response, PLAYLIST_CONTINUATION]),
        ):
            assert yt_tv.get_playlist("PLown")["description"] == "my description"

    def test_search_limit(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=SEARCH_RESPONSE):
            assert len(yt_tv.search("Oasis Wonderwall", limit=2)) == 2

    def test_get_playlist_data_api(self, yt_tv: YTMusic):
        def item(video_id: str, set_video_id: str, title: str = "Wonderwall") -> dict:
            item_id = base64.urlsafe_b64encode(f"PLown.{set_video_id}".encode()).decode().rstrip("=")
            return {
                "id": item_id,
                "snippet": {
                    "title": title,
                    "videoOwnerChannelTitle": "Oasis - Topic",
                    "videoOwnerChannelId": "UCartist",
                    "thumbnails": {"high": {"url": "h", "width": 480}, "default": {"url": "d", "width": 120}},
                },
                "contentDetails": {"videoId": video_id},
                "status": {"privacyStatus": "unlisted"},
            }

        responses = {
            ("playlistItems", None): {
                "items": [item("vid1", "56B44F6D10557CC6")],
                "nextPageToken": "PAGE2",
                "pageInfo": {"totalResults": 3},
            },
            ("playlistItems", "PAGE2"): {
                "items": [item("vid2", "289F4A46DF0A30D2"), item("gone", "017208FAA85233F9", "Deleted video")]
            },
            ("playlists", None): {
                "items": [
                    {
                        "snippet": {
                            "title": "Mine",
                            "description": "my description",
                            "channelId": "UCme",
                            "channelTitle": "me",
                        },
                        "status": {"privacyStatus": "private"},
                        "contentDetails": {"itemCount": 3},
                    }
                ]
            },
            ("channels", None): {"items": [{"id": "UCme"}]},
        }

        def data_api(method: str, resource: str, params: dict) -> dict:
            if resource == "videos":
                durations = {"vid1": "PT4M40S", "vid2": "PT1H2M3S"}
                return {
                    "items": [
                        {"id": video_id, "contentDetails": {"duration": durations[video_id]}}
                        for video_id in params["id"].split(",")
                        if video_id in durations
                    ]
                }
            return responses[(resource, params.get("pageToken"))]

        with (
            mock.patch.object(yt_tv, "_send_data_api_request", side_effect=data_api),
            mock.patch.object(yt_tv, "_send_request") as send,
        ):
            playlist = yt_tv.get_playlist("PLown", limit=None)
        send.assert_not_called()
        tracks = playlist.pop("tracks")
        assert playlist == {
            "id": "PLown",
            "owned": True,
            "privacy": "PRIVATE",
            "title": "Mine",
            "description": "my description",
            "thumbnails": [],
            "author": {"name": "me", "id": "UCme"},
            "trackCount": 3,
            "related": [],
            "duration_seconds": 280 + 3723,
        }
        assert tracks[0] == {
            "videoId": "vid1",
            "title": "Wonderwall",
            "artists": [{"name": "Oasis", "id": "UCartist"}],
            "album": None,
            "thumbnails": [{"url": "d", "width": 120}, {"url": "h", "width": 480}],
            "isAvailable": True,
            "videoType": None,
            "duration": "4:40",
            "duration_seconds": 280,
            "setVideoId": "56B44F6D10557CC6",
        }
        assert tracks[1]["duration"] == "1:02:03"
        assert [track["isAvailable"] for track in tracks] == [True, True, False]
        assert "duration" not in tracks[2]


@pytest.mark.xdist_group("playlist")
class TestOAuthLive:
    """Tests against YouTube with real OAuth credentials"""

    def test_library(self, yt_oauth_tv: YTMusic):
        playlists = yt_oauth_tv.get_library_playlists(None)
        assert "LM" in [playlist["playlistId"] for playlist in playlists]
        assert all(playlist["title"] for playlist in playlists)
        assert all(song["videoId"] and song["title"] for song in yt_oauth_tv.get_library_songs(30))
        assert all(album["playlistId"].startswith("OLAK") for album in yt_oauth_tv.get_library_albums())
        assert all(artist["artist"] for artist in yt_oauth_tv.get_library_subscriptions())

    def test_get_liked_songs(self, yt_oauth_tv: YTMusic):
        liked = yt_oauth_tv.get_liked_songs(limit=None)
        assert liked["id"] == "LM"
        assert len(liked["tracks"]) == liked["trackCount"]
        assert liked["duration_seconds"] > 0

    def test_get_playlist(self, yt_oauth_tv: YTMusic, sample_video: str):
        album = yt_oauth_tv.get_playlist("OLAK5uy_noLNRtYnrcRVVO9rOyGMx64XyjVSCz1YU", limit=None)
        assert len(album["tracks"]) == album["trackCount"] > 50
        assert not album["owned"]
        # radios are not returned by the Data API
        radio = yt_oauth_tv.get_playlist("RDAMVM" + sample_video, limit=10)
        assert len(radio["tracks"]) > 0
        with pytest.raises(YTMusicServerError):
            yt_oauth_tv.get_playlist("PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    @pytest.mark.parametrize("filter", [None, "songs", "videos", "albums", "artists", "playlists"])
    def test_search(self, yt_oauth_tv: YTMusic, filter: str | None):
        results = yt_oauth_tv.search("daft punk discovery", filter=filter, limit=10)  # type: ignore[arg-type]
        assert 0 < len(results) <= 10
        assert all(result["title"] for result in results)
        if filter:
            assert {result["resultType"] for result in results} == {filter[:-1]}

    def test_get_artist(self, yt_oauth_tv: YTMusic):
        artist = yt_oauth_tv.get_artist("UCmMUZbaYdNH0bEd1PAlAqsA")
        assert artist["name"]
        assert artist["channelId"]
        assert len(artist["sections"]) > 0
        assert all(section["contents"] for section in artist["sections"])

    def test_get_watch_playlist(self, yt_oauth_tv: YTMusic, sample_video: str):
        watch = yt_oauth_tv.get_watch_playlist(sample_video, limit=30)
        # the queue of the TV client does not always start with the requested video
        assert len(watch["tracks"]) >= 30
        assert all(track["videoId"] and track["title"] for track in watch["tracks"])
        assert watch["playlistId"] == "RDAMVM" + sample_video

    def test_unsupported(self, yt_oauth_tv: YTMusic):
        with pytest.raises(YTMusicUserError, match="not supported with OAuth"):
            yt_oauth_tv.get_history()

    def test_playlist_end2end(self, yt_oauth_tv: YTMusic, sample_video: str):
        def wait_for(condition, timeout: int = 30) -> JsonDict:
            """changes take a few seconds until they are returned"""
            deadline = time.time() + timeout
            while True:
                try:
                    playlist = yt_oauth_tv.get_playlist(playlist_id)
                    if condition(playlist):
                        return playlist
                except YTMusicServerError:
                    pass
                assert time.time() < deadline, "playlist did not reach the expected state"
                time.sleep(2)

        playlist_id = yt_oauth_tv.create_playlist(
            "test oauth", "test <b>description</b>", video_ids=[sample_video]
        )
        assert isinstance(playlist_id, str)
        try:
            playlist = wait_for(lambda p: len(p["tracks"]) == 1)
            assert playlist["owned"]
            assert playlist["privacy"] == "PRIVATE"
            assert playlist["description"] == "test description"

            response = yt_oauth_tv.add_playlist_items(playlist_id, ["bx1Bh8ZvH84", "cmpRLQZkTb8"])
            assert response["status"] == "STATUS_SUCCEEDED"  # type: ignore[index]
            response = yt_oauth_tv.edit_playlist(playlist_id, title="test oauth 2", privacyStatus="UNLISTED")
            assert response == "STATUS_SUCCEEDED"
            playlist = wait_for(lambda p: len(p["tracks"]) == 3 and p["title"] == "test oauth 2")
            assert playlist["privacy"] == "UNLISTED"
            tracks = playlist["tracks"]
            assert all(track["setVideoId"] and track["duration_seconds"] for track in tracks)

            yt_oauth_tv.edit_playlist(
                playlist_id, moveItem=(tracks[2]["setVideoId"], tracks[0]["setVideoId"])
            )
            assert yt_oauth_tv.remove_playlist_items(playlist_id, [tracks[1]]) == "STATUS_SUCCEEDED"
            playlist = wait_for(lambda p: len(p["tracks"]) == 2)
            assert [track["videoId"] for track in playlist["tracks"]] == [
                tracks[2]["videoId"],
                tracks[0]["videoId"],
            ]
        finally:
            assert yt_oauth_tv.delete_playlist(playlist_id) == "STATUS_SUCCEEDED"
