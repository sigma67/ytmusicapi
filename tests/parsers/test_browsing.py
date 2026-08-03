from copy import deepcopy

from ytmusicapi.parsers.browsing import parse_playlist

OWNED_PLAYLIST = {
    "thumbnailRenderer": {"musicThumbnailRenderer": {"thumbnail": {"thumbnails": []}}},
    "title": {
        "runs": [
            {
                "text": "Family playlist",
                "navigationEndpoint": {"browseEndpoint": {"browseId": "VLPL_family"}},
            }
        ]
    },
    "subtitle": {
        "runs": [
            {
                "text": "Owner",
                "navigationEndpoint": {"browseEndpoint": {"browseId": "UC_owner"}},
            },
            {"text": " • "},
            {"text": "1 track"},
        ]
    },
    "menu": {
        "menuRenderer": {
            "items": [
                {
                    "menuNavigationItemRenderer": {
                        "text": {"runs": [{"text": "Edit playlist"}]},
                        "navigationEndpoint": {"playlistEditorEndpoint": {"playlistId": "PL_family"}},
                    }
                }
            ]
        }
    },
}


def test_parse_playlist_marks_playlist_with_editor_endpoint_as_owned():
    playlist = parse_playlist(OWNED_PLAYLIST)

    assert playlist["owned"] is True


def test_parse_playlist_marks_playlist_without_editor_endpoint_as_not_owned():
    saved_playlist = deepcopy(OWNED_PLAYLIST)
    saved_playlist["menu"]["menuRenderer"]["items"][0]["menuNavigationItemRenderer"]["navigationEndpoint"] = {
        "watchPlaylistEndpoint": {"playlistId": "PL_family"}
    }

    playlist = parse_playlist(saved_playlist)

    assert playlist["owned"] is False
