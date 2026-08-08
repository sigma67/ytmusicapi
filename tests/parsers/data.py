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
