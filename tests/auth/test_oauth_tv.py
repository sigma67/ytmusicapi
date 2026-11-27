"""Offline tests for the TV client code path used with OAuth authentication, see #813"""

import json
import time
from unittest import mock

import pytest
from requests import Response

from ytmusicapi import OAuthCredentials, YTMusic
from ytmusicapi.auth.types import AuthType
from ytmusicapi.constants import TV_CLIENT_NAME, TV_UNSUPPORTED, TV_USER_AGENT, YT_DATA_API
from ytmusicapi.exceptions import YTMusicServerError, YTMusicUserError


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
        with mock.patch.object(
            yt_tv, "_send_request", side_effect=[PLAYLIST_RESPONSE, PLAYLIST_CONTINUATION]
        ) as send:
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
        with mock.patch.object(yt_tv, "_send_request", return_value=response):
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
        with mock.patch.object(yt_tv, "_send_request", side_effect=[response, PLAYLIST_CONTINUATION]):
            assert yt_tv.get_playlist("PLown")["description"] == "my description"

    def test_search_limit(self, yt_tv: YTMusic):
        with mock.patch.object(yt_tv, "_send_request", return_value=SEARCH_RESPONSE):
            assert len(yt_tv.search("Oasis Wonderwall", limit=2)) == 2
