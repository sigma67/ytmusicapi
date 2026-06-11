# YouTube Music Backend Endpoints Report

This report provides a brief overview of the YouTube Music API backend endpoints wrapped by `ytmusicapi`, grouped by module.

## Uploads Module
Responsible for handling `uploads` related actions.

### `get_library_upload_songs`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Returns a list of uploaded songs :param limit: How many songs to return. ``None`` retrieves them all. Default: 25 :param order: Order of songs to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of uploaded songs. Each item is in the following format:: { "entityId": "t_po_CICr2crg7OWpchDpjPjrBA", "videoId": "Uise6RPKoek", "artists": [{ 'name': 'Coldplay', 'id': 'FEmusic_library_privately_owned_artist_detaila_po_CICr2crg7OWpchIIY29sZHBsYXk', }], "title": "A Sky Full Of Stars", "album": "Ghost Stories", "likeStatus": "LIKE", "thumbnails": [...] }
- **Typical Payload Keys:** `browseId`

### `get_library_upload_albums`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the albums of uploaded songs in the user's library. :param limit: Number of albums to return. ``None`` retrives them all. Default: 25 :param order: Order of albums to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of albums as returned by :py:func:`get_library_albums`
- **Typical Payload Keys:** `browseId`

### `get_library_upload_artists`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the artists of uploaded songs in the user's library. :param limit: Number of artists to return. ``None`` retrieves them all. Default: 25 :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of artists as returned by :py:func:`get_library_artists`
- **Typical Payload Keys:** `browseId`

### `get_library_upload_artist`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Returns a list of uploaded tracks for the artist. :param browseId: Browse id of the upload artist, i.e. from :py:func:`get_library_upload_songs` :param limit: Number of songs to return (increments of 25). :return: List of uploaded songs. Example List:: [ { "entityId": "t_po_CICr2crg7OWpchDKwoakAQ", "videoId": "Dtffhy8WJgw", "title": "Hold Me (Original Mix)", "artists": [ { "name": "Jakko", "id": "FEmusic_library_privately_owned_artist_detaila_po_CICr2crg7OWpchIFamFra28" } ], "album": null, "likeStatus": "LIKE", "thumbnails": [...] } ]
- **Typical Payload Keys:** `browseId`

### `get_library_upload_album`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Get information and tracks of an album associated with uploaded tracks :param browseId: Browse id of the upload album, i.e. from i.e. from :py:func:`get_library_upload_songs` :return: Dictionary with title, description, artist and tracks. Example album:: { "title": "18 Months", "type": "Album", "thumbnails": [...], "trackCount": 7, "duration": "24 minutes", "audioPlaylistId": "MLPRb_po_55chars", "tracks": [ { "entityId": "t_po_22chars", "videoId": "FVo-UZoPygI", "title": "Feel So Close", "duration": "4:15", "duration_seconds": 255, "artists": None, "album": { "name": "18 Months", "id": "FEmusic_library_privately_owned_release_detailb_po_55chars" }, "likeStatus": "INDIFFERENT", "thumbnails": None },
- **Typical Payload Keys:** `browseId`

### `delete_upload_entity`
- **Endpoint:** `music/delete_privately_owned_entity`
- **Requires Authentication:** **Yes**
- **Description:** Deletes a previously uploaded song or album :param entityId: The entity id of the uploaded song or album, e.g. retrieved from :py:func:`get_library_upload_songs` :return: Status String or error
- **Typical Payload Keys:** `entityId`

## Podcasts Module
Responsible for handling `podcasts` related actions.

### `get_channel`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get information about a podcast channel (episodes, podcasts). For episodes, a maximum of 10 episodes are returned, the full list of episodes can be retrieved via :py:func:`get_channel_episodes` :param channelId: channel id :return: Dict containing channel info Example:: { "title": 'Stanford Graduate School of Business', "thumbnails": [...] "episodes": { "browseId": "UCGwuxdEeCf0TIA2RbPOj-8g", "results": [ { "index": 0, "title": "The Brain Gain: The Impact of Immigration on American Innovation with Rebecca Diamond", "description": "Immigrants' contributions to America ...", "duration": "24 min", "videoId": "TS3Ovvk3VAA", "browseId": "MPEDTS3Ovvk3VAA", "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE", "date": "Mar 6, 2024", "thumbnails": [...] }, ], "params": "6gPiAUdxWUJXcFlCQ3BN..." }, "podcasts": { "browseId": null, "results": [ { "title": "Stanford GSB Podcasts", "channel": { "id": "UCGwuxdEeCf0TIA2RbPOj-8g", "name": "Stanford Graduate School of Business" }, "browseId": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9", "podcastId": "PLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9", "thumbnails": [...] } ] } }
- **Typical Payload Keys:** `browseId`

### `get_channel_episodes`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get all channel episodes. This endpoint is currently unlimited :param channelId: channelId of the user :param params: params obtained by :py:func:`get_channel` :return: List of channel episodes in the format of :py:func:`get_channel` "episodes" key
- **Typical Payload Keys:** `browseId, params`

### `get_podcast`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Returns podcast metadata and episodes .. note:: To add a podcast to your library, you need to call ``rate_playlist`` on it :param playlistId: Playlist id :param limit: How many songs to return. ``None`` retrieves them all. Default: 100 :return: Dict with podcast information Example:: { "author": { "name": "Stanford Graduate School of Business", "id": "UCGwuxdEeCf0TIA2RbPOj-8g" }, "title": "Think Fast, Talk Smart: The Podcast", "description": "Join Matt Abrahams, a lecturer of...", "saved": false, "episodes": [ { "index": 0, "title": "132. Lean Into Failure: How to Make Mistakes That Work | Think Fast, Talk Smart: Communication...", "description": "Effective and productive teams and...", "duration": "25 min", "videoId": "xAEGaW2my7E", "browseId": "MPEDxAEGaW2my7E", "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE", "date": "Mar 5, 2024", "thumbnails": [...] } ] }
- **Typical Payload Keys:** `browseId`

### `get_episode`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Retrieve episode data for a single episode .. note:: To save an episode, you need to call ``add_playlist_items`` to add it to the ``SE`` (saved episodes) playlist. :param videoId: browseId (MPED..) or videoId for a single episode :return: Dict containing information about the episode The description elements are based on a custom dataclass, not shown in the example below The description text items also contain "\n" to indicate newlines, removed below due to RST issues Example:: { "author": { "name": "Stanford GSB Podcasts", "id": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9" }, "title": "124. Making Meetings Me...", "date": "Jan 16, 2024", "duration": "25 min", "saved": false, "playlistId": "MPSPPLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9", "description": [ { "text": "Delve into why people hate meetings, ... Karin Reed (" }, { "text": "https://speakerdynamics.com/team/", "url": "https://speakerdynamics.com/team/" }, { "text": ")Chapters:(" }, { "text": "00:00", "seconds": 0 }, { "text": ") Introduction Host Matt Abrahams...(" }, { "text": "01:30", "seconds": 90 }, ] }
- **Typical Payload Keys:** `browseId`

### `get_episodes_playlist`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get all episodes in an episodes playlist. Currently the only known playlist is the "New Episodes" auto-generated playlist :param playlist_id: Playlist ID, defaults to "RDPN", the id of the New Episodes playlist :return: Dictionary in the format of :py:func:`get_podcast`
- **Typical Payload Keys:** `browseId`

## Playlists Module
Responsible for handling `playlists` related actions.

### `get_playlist`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Returns a list of playlist items :param playlistId: Playlist id :param limit: How many songs to return. ``None`` retrieves them all. Default: 100 :param related: Whether to fetch 10 related playlists or not. Default: False :param suggestions_limit: How many suggestions to return. The result is a list of suggested playlist items (videos) contained in a "suggestions" key. 7 items are retrieved in each internal request. Default: 0 :return: Dictionary with information about the playlist. The key ``tracks`` contains a List of playlistItem dictionaries The result is in the following format:: { "id": "PLQwVIlKxHM6qv-o99iX9R85og7IzF9YS_", "privacy": "PUBLIC", "title": "New EDM This Week 03/13/2020", "thumbnails": [...] "description": "Weekly r/EDM new release roundup. Created with github.com/sigma67/spotifyplaylist_to_gmusic", "author": { "name": "sigmatics", "id": "..." }, "year": "2020", "duration": "6+ hours", "duration_seconds": 52651, "trackCount": 237, "suggestions": [ { "videoId": "HLCsfOykA94", "title": "Mambo (GATTÜSO Remix)", "artists": [{ "name": "Nikki Vianna", "id": "UCMW5eSIO1moVlIBLQzq4PnQ" }], "album": { "name": "Mambo (GATTÜSO Remix)", "id": "MPREb_jLeQJsd7U9w" }, "likeStatus": "LIKE", "thumbnails": [...], "isAvailable": true, "isExplicit": false, "duration": "3:32", "duration_seconds": 212, "setVideoId": "to_be_updated_by_client" } ], "related": [ { "title": "Presenting MYRNE", "playlistId": "RDCLAK5uy_mbdO3_xdD4NtU1rWI0OmvRSRZ8NH4uJCM", "thumbnails": [...], "description": "Playlist • YouTube Music" } ], "tracks": [ { "videoId": "bjGppZKiuFE", "title": "Lost", "artists": [ { "name": "Guest Who", "id": "UCkgCRdnnqWnUeIH7EIc3dBg" }, { "name": "Kate Wild", "id": "UCwR2l3JfJbvB6aq0RnnJfWg" } ], "album": { "name": "Lost", "id": "MPREb_PxmzvDuqOnC" }, "duration": "2:58", "duration_seconds": 178, "setVideoId": "748EE8..." "likeStatus": "INDIFFERENT", "thumbnails": [...], "isAvailable": True, "isExplicit": False, "videoType": "MUSIC_VIDEO_TYPE_OMV", "inLibrary": False, "feedbackTokens": { "add": "AB9zfpJxtvrU...", "remove": "AB9zfpKTyZ..." }, "pinnedToListenAgain": False, "listenAgainFeedbackTokens": { "pin": "AB9zfpImL2k...", "unpin": "AB9zfpJt6pA..." }, "communityVoteStatus": { "netVoteValue": 12, "status": "VOTE_STATUS_UPVOTED"" } } "creditsBrowseId": "MPTCekz1IJ9I0sw" ] } The setVideoId is the unique id of this playlist item and needed for moving/removing playlist items Note that communityVoteStatus can be null if the information is not available (i.e. playlist does not have that setting enabled, the request is not authenticated, ...) Collaborative playlists replace ``author`` with limited data about ``collaborators``:: { "collaborators": { "text": "by Sample Author and 1 other", "avatars": [ { "url": "https://yt3.ggpht.com/sample-author-photo" }, { "url": "https://yt3.ggpht.com/sample-collaborator-photo" } ] } }
- **Typical Payload Keys:** `browseId`

### `create_playlist`
- **Endpoint:** `playlist/create`
- **Requires Authentication:** **Yes**
- **Description:** Creates a new empty playlist and returns its id. :param title: Playlist title :param description: Playlist description :param privacy_status: Playlists can be ``PUBLIC``, ``PRIVATE``, or ``UNLISTED``. Default: ``PRIVATE`` :param video_ids: IDs of songs to create the playlist with :param source_playlist: Another playlist whose songs should be added to the new playlist :return: ID of the YouTube playlist or full response if there was an error

### `join_collaborative_playlist`
- **Endpoint:** `browse/edit_playlist`
- **Requires Authentication:** **Yes**
- **Description:** Given an invite token, join a collaborative playlist and add it to your library. :param playlistId: ID of the playlist to join. If you're already a collaborator, an Unauthorized server error is raised. :param joinCollaborationToken: See :py:func:`edit_playlist`, or ``jct`` in YTM's invite URL :return: Status String or full response

### `edit_playlist`
- **Endpoint:** `browse/edit_playlist`
- **Requires Authentication:** **Yes**
- **Description:** Edit title, description or privacyStatus of a playlist. You may also move an item within a playlist or append another playlist to this playlist. :param playlistId: Playlist id :param title: Optional. New title for the playlist :param description: Optional. New description for the playlist :param privacyStatus: Optional. New privacy status for the playlist :param collaboration: Optional. Enable or disable collaboration. If False and collaboration is not enabled, a Forbidden server error is raised. If True, a new ``joinCollaborationToken`` is returned. Collaborators cannot interact with private playlists. :param moveItem: Optional. Move one item before another. Items are specified by setVideoId, which is the unique id of this playlist item. See :py:func:`get_playlist` :param addPlaylistId: Optional. Id of another playlist to add to this playlist :param sortOrder: Optional. Change the order tracks are returned in. The default is ``MANUAL``. :param addToTop: Optional. Change the state of this playlist to add items to the top of the playlist (if True) or the bottom of the playlist (if False - this is also the default of a new playlist). :param VoteOption: Optional. Change who can participate in community voting in this playlist. Note that a bad request will be thrown if voteOption is PlaylistVoteEditOptions.COLLABORATORS_ONLY but the playlist is not enabled for collaboration prior to the edit. :return: Status String, ``collaboration`` dict described below, or full response Dictionary returned when ``collaboration`` is True and the request is successful:: { "status": "STATUS_SUCCEEDED", "joinCollaborationToken": "kM9wXdRj2p8v_qL3sHBkTz" }

### `delete_playlist`
- **Endpoint:** `playlist/delete`
- **Requires Authentication:** **Yes**
- **Description:** Delete a playlist. :param playlistId: Playlist id :return: Status String or full response
- **Typical Payload Keys:** `playlistId`

### `add_playlist_items`
- **Endpoint:** `browse/edit_playlist`
- **Requires Authentication:** **Yes**
- **Description:** Add songs to an existing playlist :param playlistId: Playlist id :param videoIds: List of Video ids :param source_playlist: Playlist id of a playlist to add to the current playlist (no duplicate check) :param duplicates: If True, duplicates will be added. If False, an error will be returned if there are duplicates (no items are added to the playlist) :return: Status String and a dict containing the new setVideoId for each videoId or full response

### `remove_playlist_items`
- **Endpoint:** `browse/edit_playlist`
- **Requires Authentication:** **Yes**
- **Description:** Remove songs from an existing playlist :param playlistId: Playlist id :param videos: List of PlaylistItems, see :py:func:`get_playlist`. Must contain videoId and setVideoId :return: Status String or full response

## Charts Module
Responsible for handling `charts` related actions.

### `get_charts`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get latest charts data from YouTube Music: Artists and playlists of top videos. Unauthenticated requests return unranked Artists with "rank" and "trend" set to None. US charts have an extra Genres section with some Genre charts. :param country: ISO 3166-1 Alpha-2 country code. Default: ``ZZ`` = Global :return: Dictionary containing chart video playlists (with separate daily/weekly charts if authenticated with a premium account), chart genres (US-only), and chart artists. Example:: { "countries": { "selected": { "text": "United States" }, "options": ["DE", "ZZ", "ZW"] }, "videos": [ { "title": "Daily Top Music Videos - United States", "playlistId": "PL4fGSI1pDJn61unMfmrUSz68RT8IFFnks", "thumbnails": [] } ], "artists": [ { "title": "YoungBoy Never Broke Again", "browseId": "UCR28YDxjDE3ogQROaNdnRbQ", "subscribers": "9.62M", "thumbnails": [], "rank": "1", "trend": "neutral" } ], "genres": [ { "title": "Top 50 Pop Music Videos United States", "playlistId": "PL4fGSI1pDJn77aK7sAW2AT0oOzo5inWY8", "thumbnails": [] } ] }

## Library Module
Responsible for handling `library` related actions.

### `get_library_playlists`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Retrieves the playlists in the user's library. :param limit: Number of playlists to retrieve. ``None`` retrieves them all. :return: List of owned playlists. Each item is in the following format:: { 'playlistId': 'PLQwVIlKxHM6rz0fDJVv_0UlXGEWf-bFys', 'title': 'Playlist title', 'thumbnails: [...], 'count': 5 }
- **Typical Payload Keys:** `browseId`

### `get_library_songs`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the songs in the user's library (liked videos are not included). To get liked songs and videos, use :py:func:`get_liked_songs` :param limit: Number of songs to retrieve :param validate_responses: Flag indicating if responses from YTM should be validated and retried in case when some songs are missing. Default: False :param order: Order of songs to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of songs. Same format as :py:func:`get_playlist`
- **Typical Payload Keys:** `browseId`

### `get_library_albums`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the albums in the user's library. :param limit: Number of albums to return :param order: Order of albums to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of albums. Each item is in the following format:: { "browseId": "MPREb_G8AiyN7RvFg", "playlistId": "OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc", "title": "Beautiful", "type": "Album", "thumbnails": [...], "artists": [{ "name": "Project 46", "id": "UCXFv36m62USAN5rnVct9B4g" }], "year": "2015" }
- **Typical Payload Keys:** `browseId`

### `get_library_artists`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the artists of the songs in the user's library. :param limit: Number of artists to return :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of artists. Each item is in the following format:: { "browseId": "UCxEqaQWosMHaTih-tgzDqug", "artist": "WildVibes", "subscribers": "2.91K", "thumbnails": [...] }
- **Typical Payload Keys:** `browseId`

### `get_library_subscriptions`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets the artists the user has subscribed to. :param limit: Number of artists to return :param order: Order of artists to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of artists. Same format as :py:func:`get_library_artists`
- **Typical Payload Keys:** `browseId`

### `get_library_podcasts`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Get podcasts the user has added to the library :param limit: Number of podcasts to return :param order: Order of podcasts to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of podcasts. New Episodes playlist is the first podcast returned, but only if subscribed to relevant podcasts. Example:: [ { "title": "New Episodes", "channel": { "id": null, "name": "Auto playlist" }, "browseId": "VLRDPN", "podcastId": "RDPN", "thumbnails": [...] }, { "title": "5 Minuten Harry Podcast", "channel": { "id": "UCDIDXF4WM1qQzerrxeEfSdA", "name": "coldmirror" }, "browseId": "MPSPPLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH", "podcastId": "PLDvBqWb1UAGeEt9n6vFH_zdGw65Obf3sH", "thumbnails": [...] } ]
- **Typical Payload Keys:** `browseId`

### `get_library_channels`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Get channels the user has added to the library :param limit: Number of channels to return :param order: Order of channels to return. Allowed values: ``a_to_z``, ``z_to_a``, ``recently_added``. Default: Default order. :return: List of channels. Example:: [ { "browseId": "UCRFF8xw5dg9mL4r5ryFOtKw", "artist": "Jumpers Jump", "subscribers": "1.54M", "thumbnails": [...] }, { "browseId": "UCQ3f2_sO3NJyDkuCxCNSOVA", "artist": "BROWN BAG", "subscribers": "74.2K", "thumbnails": [...] } ]
- **Typical Payload Keys:** `browseId`

### `get_history`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Gets your play history in reverse chronological order :return: List of playlistItems, see :py:func:`get_playlist` The additional property ``played`` indicates when the playlistItem was played The additional property ``feedbackToken`` can be used to remove items with :py:func:`remove_history_items`
- **Typical Payload Keys:** `browseId`

### `remove_history_items`
- **Endpoint:** `feedback`
- **Requires Authentication:** **Yes**
- **Description:** Remove an item from the account's history. This method does currently not work with brand accounts :param feedbackTokens: Token to identify the item to remove, obtained from :py:func:`get_history` :return: Full response
- **Typical Payload Keys:** `feedbackTokens`

### `edit_song_library_status`
- **Endpoint:** `feedback`
- **Requires Authentication:** **Yes**
- **Description:** Depending on the provided tokens: - Adds or removes songs from your library - Pins or unpins content from the "Listen Again" carousel :param feedbackTokens: List of feedbackTokens obtained from authenticated requests to endpoints that return songs (i.e. :py:func:`get_album`) :return: Full response .. warning:: Due to a YouTube Music bug, content might not be unpinned from "Listen Again".
- **Typical Payload Keys:** `feedbackTokens`

### `subscribe_artists`
- **Endpoint:** `subscription/subscribe`
- **Requires Authentication:** **Yes**
- **Description:** Subscribe to artists. Adds the artists to your library :param channelIds: Artist channel ids :return: Full response
- **Typical Payload Keys:** `channelIds`

### `unsubscribe_artists`
- **Endpoint:** `subscription/unsubscribe`
- **Requires Authentication:** **Yes**
- **Description:** Unsubscribe from artists. Removes the artists from your library :param channelIds: Artist channel ids :return: Full response
- **Typical Payload Keys:** `channelIds`

### `get_account_info`
- **Endpoint:** `account/account_menu`
- **Requires Authentication:** **Yes**
- **Description:** Gets information about the currently authenticated user's account. :return: Dictionary with user's account name, channel handle, and URL of their account photo. Example:: { "accountName": "Sample User", "channelHandle": "@SampleUser "accountPhotoUrl": "https://yt3.ggpht.com/sample-user-photo" }

## Browsing Module
Responsible for handling `browsing` related actions.

### `get_home`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get the home page. The home page is structured as titled rows, returning 3 rows of music suggestions at a time. Content varies and may contain artist, album, song or playlist suggestions, sometimes mixed within the same row :param limit: Number of rows on the home page to return :return: List of dictionaries keyed with 'title' text and 'contents' list Example list:: [ { "title": "Your morning music", "contents": [ { //album result "title": "Sentiment", "browseId": "MPREb_QtqXtd2xZMR", "thumbnails": [...] }, { //playlist result "title": "r/EDM top submissions 01/28/2022", "playlistId": "PLz7-xrYmULdSLRZGk-6GKUtaBZcgQNwel", "thumbnails": [...], "description": "redditEDM • 161 songs", "count": "161", "author": [ { "name": "redditEDM", "id": "UCaTrZ9tPiIGHrkCe5bxOGwA" } ] } ] }, { "title": "Your favorites", "contents": [ { //artist result "title": "Chill Satellite", "browseId": "UCrPLFBWdOroD57bkqPbZJog", "subscribers": "374", "thumbnails": [...] } { //album result "title": "Dragon", "year": "Two Steps From Hell", "browseId": "MPREb_M9aDqLRbSeg", "thumbnails": [...] } ] }, { "title": "Quick picks", "contents": [ { //song quick pick "title": "Gravity", "videoId": "EludZd6lfts", "artists": [{ "name": "yetep", "id": "UCSW0r7dClqCoCvQeqXiZBlg" }], "thumbnails": [...], "album": { "name": "Gravity", "id": "MPREb_D6bICFcuuRY" } }, { //video quick pick "title": "Gryffin & Illenium (feat. Daya) - Feel Good (L3V3LS Remix)", "videoId": "bR5l0hJDnX8", "artists": [ { "name": "L3V3LS", "id": "UCCVNihbOdkOWw_-ajIYhAbQ" } ], "thumbnails": [...], "views": "10M" } ] } ]
- **Typical Payload Keys:** `browseId`

### `get_artist`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get information about an artist and their top releases (songs, albums, singles, videos, and related artists). The top lists contain pointers for getting the full list of releases. Possible content types for get_artist are: - songs - albums - singles - shows - videos - episodes - podcasts - related Each of these content keys in the response contains ``results`` and possibly ``browseId`` and ``params``. - For songs/videos, pass the browseId to :py:func:`get_playlist`. - For albums/singles/shows, pass browseId and params to :py:func:`get_artist_albums`. :param channelId: channel id of the artist :return: Dictionary with requested information. .. warning:: The returned channelId is not the same as the one passed to the function. It should be used only with :py:func:`subscribe_artists`. Example:: { "description": "Oasis were ...", "descriptionRuns": [ { "text":"Oasis were ..." } ], "views": "3,693,390,359 views", "name": "Oasis", "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q", "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg", "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg", "subscribers": "3.86M", "monthlyListeners": "29.1M", "subscribed": false, "thumbnails": [...], "songs": { "browseId": "VLPLMpM3Z0118S42R1npOhcjoakLIv1aqnS1", "results": [ { "videoId": "ZrOKjDZOtkA", "title": "Wonderwall (Remastered)", "thumbnails": [...], "artist": "Oasis", "album": "(What's The Story) Morning Glory? (Remastered)" } ] }, "albums": { "results": [ { "title": "Familiar To Millions", "thumbnails": [...], "year": "2018", "browseId": "MPREb_AYetWMZunqA" } ], "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA", "params": "6gPTAUNwc0JDbndLYlFBQV..." }, "singles": { "results": [ { "title": "Stand By Me (Mustique Demo)", "thumbnails": [...], "type": "Single", "year": "2016", "browseId": "MPREb_7MPKLhibN5G" } ], "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA", "params": "6gPTAUNwc0JDbndLYlFBQV..." }, "videos": { "results": [ { "title": "Wonderwall", "thumbnails": [...], "views": "358M", "videoId": "bx1Bh8ZvH84", "playlistId": "PLMpM3Z0118S5xuNckw1HUcj1D021AnMEB" } ], "browseId": "VLPLMpM3Z0118S5xuNckw1HUcj1D021AnMEB" }, "related": { "results": [ { "browseId": "UCt2KxZpY5D__kapeQ8cauQw", "subscribers": "450K", "title": "The Verve" }, { "browseId": "UCwK2Grm574W1u-sBzLikldQ", "subscribers": "341K", "title": "Liam Gallagher" }, ... ] } } The difference between description and descriptionRuns is that description is just the raw text of the description and does not have any knowledge of the hyperlinks in the description. Whereas descriptionRuns is a list of dictionaries which contains the text runs of the description that is aware of the hyperlinks in the description. There are two types of text runs. 1. PlainText: which has format {"text": string} 2. HyperLink: which has format {"text": string, "url": string}
- **Typical Payload Keys:** `browseId`

### `get_artist_albums`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get the full list of an artist's albums, singles or shows :param channelId: browseId of the artist as returned by :py:func:`get_artist` :param params: params obtained by :py:func:`get_artist` :param limit: Number of albums to return. ``None`` retrieves them all. Default: 100 :param order: Order of albums to return. Allowed values: ``Recency``, ``Popularity``, `Alphabetical order`. Default: Default order. :return: List of albums in the format of :py:func:`get_library_albums`, except artists key is missing.
- **Typical Payload Keys:** `browseId, params`

### `get_user`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Retrieve a user's page. A user may own videos or playlists. Use :py:func:`get_user_playlists` to retrieve all playlists:: result = get_user(channelId) get_user_playlists(channelId, result["playlists"]["params"]) Similarly, use :py:func:`get_user_videos` to retrieve all videos:: get_user_videos(channelId, result["videos"]["params"]) :param channelId: channelId of the user :return: Dictionary with information about a user. Example:: { "name": "4Tune - No Copyright Music", "videos": { "browseId": "UC44hbeRoCZVVMVg5z0FfIww", "results": [ { "title": "Epic Music Soundtracks 2019", "videoId": "bJonJjgS2mM", "playlistId": "RDAMVMbJonJjgS2mM", "thumbnails": [ { "url": "https://i.ytimg.com/vi/bJon...", "width": 800, "height": 450 } ], "views": "19K" } ] }, "playlists": { "browseId": "UC44hbeRoCZVVMVg5z0FfIww", "results": [ { "title": "♚ Machinimasound | Playlist", "playlistId": "PLRm766YvPiO9ZqkBuEzSTt6Bk4eWIr3gB", "thumbnails": [ { "url": "https://i.ytimg.com/vi/...", "width": 400, "height": 225 } ] } ], "params": "6gO3AUNvWU..." } }
- **Typical Payload Keys:** `browseId`

### `get_user_playlists`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Retrieve a list of playlists for a given user. Call this function again with the returned ``params`` to get the full list. :param channelId: channelId of the user. :param params: params obtained by :py:func:`get_user` :return: List of user playlists in the format of :py:func:`get_library_playlists`
- **Typical Payload Keys:** `browseId, params`

### `get_user_videos`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Retrieve a list of videos for a given user. Call this function again with the returned ``params`` to get the full list. :param channelId: channelId of the user. :param params: params obtained by :py:func:`get_user` :return: List of user videos
- **Typical Payload Keys:** `browseId, params`

### `get_album`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get information and tracks of an album :param browseId: browseId of the album, for example returned by :py:func:`search` :return: Dictionary with album and track metadata. The result is in the following format:: { "title": "Revival", "type": "Album", "thumbnails": [], "description": "Revival is the...", "descriptionRuns": [ {"text": "Revival is the..."}, ], "artists": [ { "name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ" } ], "year": "2017", "trackCount": 19, "duration": "1 hour, 17 minutes", "audioPlaylistId": "OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY", "tracks": [ { "videoId": "iKLU7z_xdYQ", "title": "Walk On Water (feat. Beyoncé)", "artists": [ { "name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ" } ], "album": "Revival", "likeStatus": "INDIFFERENT", "thumbnails": null, "isAvailable": true, "isExplicit": true, "duration": "5:03", "duration_seconds": 303, "trackNumber": 0, "inLibrary": false, "feedbackTokens": { "add": "AB9zfpK...", "remove": "AB9zfpK..." }, "pinnedToListenAgain": false, "listenAgainFeedbackTokens": { "pin": "AB9zfpJ...", "unpin": "AB9zfpL..." }, "creditsBrowseId": "MPTCiKLU7z_xdYQ" } ], "other_versions": [ { "title": "Revival", "year": "Eminem", "browseId": "MPREb_fefKFOTEZSp", "thumbnails": [...], "isExplicit": false }, ], "duration_seconds": 4657 } For the distinction between description and descriptionRuns. Please refer to get_artist.
- **Typical Payload Keys:** `browseId`

### `get_song_credits`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get credits for a song. Top-level entries are limited to ``performed_by``, ``written_by``, ``produced_by`` and ``music_metadata_provided_by``. If YouTube returns additional data, it will be returned in ``other_sections``. :param browseId: browseId for the credits of a song, for example returned as ``creditsBrowseId`` in the tracks of :py:func:`get_album` :return: Dictionary with credit sections. Example:: { "performed_by": { "localized_title": "Performed by" "data": [ "Eminem", "Beyoncé" ] }, "written_by": { "localized_title": "Written by", "data": [ "Marshall Mathers", "Beyoncé Knowles", "Holly Hafermann" ] }, "produced_by": { "localized_title": "Produced by", "data": [ "Rick Rubin" ] }, "music_metadata_provided_by": { "localized_title": "Music metadata provided by" "data": [ "Eminem Catalog PS" ] }, "other_sections": [ { "localized_title": "Piano", "data": [ "Skylar Grey" ] } ] }
- **Typical Payload Keys:** `browseId`

### `get_song`
- **Endpoint:** `player`
- **Requires Authentication:** No
- **Description:** Returns metadata and streaming information about a song or video. :param videoId: Video id :param signatureTimestamp: Provide the current YouTube signatureTimestamp. If not provided a default value will be used, which might result in invalid streaming URLs :return: Dictionary with song metadata. Example:: { "playabilityStatus": { "status": "OK", "playableInEmbed": true, "audioOnlyPlayability": { "audioOnlyPlayabilityRenderer": { "trackingParams": "CAEQx2kiEwiuv9X5i5H1AhWBvlUKHRoZAHk=", "audioOnlyAvailability": "FEATURE_AVAILABILITY_ALLOWED" } }, "miniplayer": { "miniplayerRenderer": { "playbackMode": "PLAYBACK_MODE_ALLOW" } }, "contextParams": "Q0FBU0FnZ0M=" }, "streamingData": { "expiresInSeconds": "21540", "adaptiveFormats": [ { "itag": 140, "url": "https://rr1---sn-h0jelnez.c.youtube.com/videoplayback?expire=1641080272...", "mimeType": "audio/mp4; codecs="mp4a.40.2"", "bitrate": 131007, "initRange": { "start": "0", "end": "667" }, "indexRange": { "start": "668", "end": "999" }, "lastModified": "1620321966927796", "contentLength": "3967382", "quality": "tiny", "projectionType": "RECTANGULAR", "averageBitrate": 129547, "highReplication": true, "audioQuality": "AUDIO_QUALITY_MEDIUM", "approxDurationMs": "245000", "audioSampleRate": "44100", "audioChannels": 2, "loudnessDb": -1.3000002 } ] }, "playbackTracking": { "videostatsPlaybackUrl": { "baseUrl": "https://s.youtube.com/api/stats/playback?cl=491307275&docid=AjXQiKP5kMs&ei=Nl2HY-6MH5WE8gPjnYnoDg&fexp=1714242%2C9405963%2C23804281%2C23858057%2C23880830%2C23880833%2C23882685%2C23918597%2C23934970%2C23946420%2C23966208%2C23983296%2C23998056%2C24001373%2C24002022%2C24002025%2C24004644%2C24007246%2C24034168%2C24036947%2C24077241%2C24080738%2C24120820%2C24135310%2C24135692%2C24140247%2C24161116%2C24162919%2C24164186%2C24169501%2C24175560%2C24181174%2C24187043%2C24187377%2C24187854%2C24191629%2C24197450%2C24199724%2C24200839%2C24209349%2C24211178%2C24217535%2C24219713%2C24224266%2C24241378%2C24248091%2C24248956%2C24255543%2C24255545%2C24262346%2C24263796%2C24265426%2C24267564%2C24268142%2C24279196%2C24280220%2C24283426%2C24283493%2C24287327%2C24288045%2C24290971%2C24292955%2C24293803%2C24299747%2C24390674%2C24391018%2C24391537%2C24391709%2C24392268%2C24392363%2C24392401%2C24401557%2C24402891%2C24403794%2C24406605%2C24407200%2C24407665%2C24407914%2C24408220%2C24411766%2C24413105%2C24413820%2C24414162%2C24415866%2C24416354%2C24420756%2C24421162%2C24425861%2C24428962%2C24590921%2C39322504%2C39322574%2C39322694%2C39322707&ns=yt&plid=AAXusD4TIOMjS5N4&el=detailpage&len=246&of=Jx1iRksbq-rB9N1KSijZLQ&osid=MWU2NzBjYTI%3AAOeUNAagU8UyWDUJIki5raGHy29-60-yTA&uga=29&vm=CAEQABgEOjJBUEV3RWxUNmYzMXNMMC1MYVpCVnRZTmZWMWw1OWVZX2ZOcUtCSkphQ245VFZwOXdTQWJbQVBta0tETEpWNXI1SlNIWEJERXdHeFhXZVllNXBUemt5UHR4WWZEVzFDblFUSmdla3BKX2R0dXk3bzFORWNBZmU5YmpYZnlzb3doUE5UU0FoVGRWa0xIaXJqSWgB", "headers": [ { "headerType": "USER_AUTH" }, { "headerType": "VISITOR_ID" }, { "headerType": "PLUS_PAGE_ID" } ] }, "videostatsDelayplayUrl": {(as above)}, "videostatsWatchtimeUrl": {(as above)}, "ptrackingUrl": {(as above)}, "qoeUrl": {(as above)}, "atrUrl": {(as above)}, "videostatsScheduledFlushWalltimeSeconds": [ 10, 20, 30 ], "videostatsDefaultFlushIntervalSeconds": 40 }, "videoDetails": { "videoId": "AjXQiKP5kMs", "title": "Sparks", "lengthSeconds": "245", "channelId": "UCvCk2zFqkCYzpnSgWfx0qOg", "isOwnerViewing": false, "isCrawlable": false, "thumbnail": { "thumbnails": [] }, "allowRatings": true, "viewCount": "12", "author": "Thomas Bergersen", "isPrivate": true, "isUnpluggedCorpus": false, "musicVideoType": "MUSIC_VIDEO_TYPE_PRIVATELY_OWNED_TRACK", "isLiveContent": false }, "microformat": { "microformatDataRenderer": { "urlCanonical": "https://music.youtube.com/watch?v=AjXQiKP5kMs", "title": "Sparks - YouTube Music", "description": "Uploaded to YouTube via YouTube Music Sparks", "thumbnail": { "thumbnails": [ { "url": "https://i.ytimg.com/vi/AjXQiKP5kMs/hqdefault.jpg", "width": 480, "height": 360 } ] }, "siteName": "YouTube Music", "appName": "YouTube Music", "androidPackage": "com.google.android.apps.youtube.music", "iosAppStoreId": "1017492454", "iosAppArguments": "https://music.youtube.com/watch?v=AjXQiKP5kMs", "ogType": "video.other", "urlApplinksIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks", "urlApplinksAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=applinks", "urlTwitterIos": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link", "urlTwitterAndroid": "vnd.youtube.music://music.youtube.com/watch?v=AjXQiKP5kMs&feature=twitter-deep-link", "twitterCardType": "player", "twitterSiteHandle": "@YouTubeMusic", "schemaDotOrgType": "http://schema.org/VideoObject", "noindex": true, "unlisted": true, "paid": false, "familySafe": true, "pageOwnerDetails": { "name": "Music Library Uploads", "externalChannelId": "UCvCk2zFqkCYzpnSgWfx0qOg", "youtubeProfileUrl": "http://www.youtube.com/channel/UCvCk2zFqkCYzpnSgWfx0qOg" }, "videoDetails": { "externalVideoId": "AjXQiKP5kMs", "durationSeconds": "246", "durationIso8601": "PT4M6S" }, "linkAlternates": [ { "hrefUrl": "android-app://com.google.android.youtube/http/youtube.com/watch?v=AjXQiKP5kMs" }, { "hrefUrl": "ios-app://544007664/http/youtube.com/watch?v=AjXQiKP5kMs" }, { "hrefUrl": "https://www.youtube.com/oembed?format=json&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs", "title": "Sparks", "alternateType": "application/json+oembed" }, { "hrefUrl": "https://www.youtube.com/oembed?format=xml&url=https%3A%2F%2Fmusic.youtube.com%2Fwatch%3Fv%3DAjXQiKP5kMs", "title": "Sparks", "alternateType": "text/xml+oembed" } ], "viewCount": "12", "publishDate": "1969-12-31", "category": "Music", "uploadDate": "1969-12-31" } } }

### `get_song_related`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Gets related content for a song. Equivalent to the content shown in the "Related" tab of the watch panel. :param browseId: The ``related`` key in the ``get_watch_playlist`` response. Example:: [ { "title": "You might also like", "contents": [ { "title": "High And Dry", "videoId": "7fv84nPfTH0", "artists": [{ "name": "Radiohead", "id": "UCr_iyUANcn9OX_yy9piYoLw" }], "thumbnails": [ { "url": "https://lh3.googleusercontent.com/TWWT47cHLv3yAugk4h9eOzQ46FHmXc_g-KmBVy2d4sbg_F-Gv6xrPglztRVzp8D_l-yzOnvh-QToM8s=w60-h60-l90-rj", "width": 60, "height": 60 } ], "isExplicit": false, "album": { "name": "The Bends", "id": "MPREb_xsmDKhqhQrG" } } ] }, { "title": "Recommended playlists", "contents": [ { "title": "'90s Alternative Rock Hits", "playlistId": "RDCLAK5uy_m_h-nx7OCFaq9AlyXv78lG0AuloqW_NUA", "thumbnails": [...], "description": "Playlist • YouTube Music" } ] }, { "title": "Similar artists", "contents": [ { "title": "Noel Gallagher", "browseId": "UCu7yYcX_wIZgG9azR3PqrxA", "subscribers": "302K", "thumbnails": [...] } ] }, { "title": "Oasis", "contents": [ { "title": "Shakermaker", "year": "2014", "browseId": "MPREb_WNGQWp5czjD", "thumbnails": [...] } ] }, { "title": "About the artist", "contents": "Oasis were a rock band consisting of Liam Gallagher, Paul ... (full description shortened for documentation)" } ]

### `get_lyrics`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Returns lyrics of a song or video. When `timestamps` is set, lyrics are returned with timestamps, if available. :param browseId: Lyrics browseId obtained from :py:func:`get_watch_playlist` (startswith ``MPLYt...``). :param timestamps: Optional. Whether to return bare lyrics or lyrics with timestamps, if available. (Default: `False`) :return: Dictionary with song lyrics or ``None``, if no lyrics are found. The ``hasTimestamps``-key determines the format of the data. Example when `timestamps=False`, or no timestamps are available:: { "lyrics": "Today is gonna be the day\nThat they're gonna throw it back to you\n", "source": "Source: LyricFind", "hasTimestamps": False } Example when `timestamps` is set to `True` and timestamps are available:: { "lyrics": [ LyricLine( text="I was a liar", start_time=9200, end_time=10630, id=1 ), LyricLine( text="I gave in to the fire", start_time=10680, end_time=12540, id=2 ), ], "source": "Source: LyricFind", "hasTimestamps": True }

### `get_tasteprofile`
- **Endpoint:** `browse`
- **Requires Authentication:** **Yes**
- **Description:** Fetches suggested artists from taste profile (music.youtube.com/tasteprofile). Must be authenticated. Tasteprofile allows users to pick artists to update their recommendations. Only returns a list of suggested artists, not the actual list of selected entries :return: Dictionary with artist and their selection & impression value Example:: { "Drake": { "selectionValue": "tastebuilder_selection=/m/05mt_q" "impressionValue": "tastebuilder_impression=/m/05mt_q" } }

### `set_tasteprofile`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Favorites artists to see more recommendations from the artist. Use :py:func:`get_tasteprofile` to see which artists are available to be recommended :param artists: A List with names of artists, must be contained in the tasteprofile :param taste_profile: tasteprofile result from :py:func:`get_tasteprofile`. Pass this if you call :py:func:`get_tasteprofile` anyway to save an extra request. :return: None if successful
- **Typical Payload Keys:** `browseId, formData`

## Watch Module
Responsible for handling `watch` related actions.

### `get_watch_playlist`
- **Endpoint:** `next`
- **Requires Authentication:** No
- **Description:** Get a watch list of tracks. This watch playlist appears when you press play on a track in YouTube Music. Please note that the ``INDIFFERENT`` likeStatus of tracks returned by this endpoint may be either ``INDIFFERENT`` or ``DISLIKE``, due to ambiguous data returned by YouTube Music. :param videoId: videoId of the played video :param playlistId: playlistId of the played playlist or album :param limit: minimum number of watch playlist items to return :param radio: get a radio playlist (changes each time) :param shuffle: shuffle the input playlist. only works when the playlistId parameter is set at the same time. does not work if radio=True :return: List of watch playlist items. The counterpart key is optional and only appears if a song has a corresponding video counterpart (UI song/video switcher). Example:: { "tracks": [ { "videoId": "9mWr4c_ig54", "title": "Foolish Of Me (feat. Jonathan Mendelsohn)", "length": "3:07", "thumbnail": [ { "url": "https://lh3.googleusercontent.com/ulK2YaLtOW0PzcN7ufltG6e4ae3WZ9Bvg8CCwhe6LOccu1lCKxJy2r5AsYrsHeMBSLrGJCNpJqXgwczk=w60-h60-l90-rj", "width": 60, "height": 60 }... ], "inLibrary": false, "feedbackTokens": { "add": "AB9zfpIGg9XN4u2iJ...", "remove": "AB9zfpJdzWLcdZtC..." }, "pinnedToListenAgain": true, "listenAgainFeedbackTokens": { "pin": "AB9zfpK8kP5mQ7rT...", "unpin": "AB9zfpLy3L9vB2xN..." }, "likeStatus": "INDIFFERENT", "videoType": "MUSIC_VIDEO_TYPE_ATV", "artists": [ { "name": "Seven Lions", "id": "UCYd2yzYRx7b9FYnBSlbnknA" }, { "name": "Jason Ross", "id": "UCVCD9Iwnqn2ipN9JIF6B-nA" }, { "name": "Crystal Skies", "id": "UCTJZESxeZ0J_M7JXyFUVmvA" } ], "album": { "name": "Foolish Of Me", "id": "MPREb_C8aRK1qmsDJ" }, "year": "2020", "counterpart": { "videoId": "E0S4W34zFMA", "title": "Foolish Of Me [ABGT404] (feat. Jonathan Mendelsohn)", "length": "3:07", "thumbnail": [...], "feedbackTokens": null, "likeStatus": "LIKE", "artists": [ { "name": "Jason Ross", "id": null }, { "name": "Seven Lions", "id": null }, { "name": "Crystal Skies", "id": null } ], "views": "6.6K" } },... ], "playlistId": "RDAMVM4y33h81phKU", "lyrics": "MPLYt_HNNclO0Ddoc-17" }
- **Typical Payload Keys:** `enablePersistentPlaylistPanel, isAudioOnly, tunerSettingValue`

## Explore Module
Responsible for handling `explore` related actions.

### `get_mood_categories`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Fetch "Moods & Genres" categories from YouTube Music. :return: Dictionary of sections and categories. Example:: { 'For you': [ { 'params': 'ggMPOg1uX1ZwN0pHT2NBT1Fk', 'title': '1980s' }, { 'params': 'ggMPOg1uXzZQbDB5eThLRTQ3', 'title': 'Feel Good' }, ... ], 'Genres': [ { 'params': 'ggMPOg1uXzVLbmZnaWI4STNs', 'title': 'Dance & Electronic' }, { 'params': 'ggMPOg1uX3NjZllsNGVEMkZo', 'title': 'Decades' }, ... ], 'Moods & moments': [ { 'params': 'ggMPOg1uXzVuc0dnZlhpV3Ba', 'title': 'Chill' }, { 'params': 'ggMPOg1uX2ozUHlwbWM3ajNq', 'title': 'Commute' }, ... ], }

### `get_mood_playlists`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Retrieve a list of playlists for a given "Moods & Genres" category. :param params: params obtained by :py:func:`get_mood_categories` :return: List of playlists in the format of :py:func:`get_library_playlists`

### `get_explore`
- **Endpoint:** `browse`
- **Requires Authentication:** No
- **Description:** Get latest explore data from YouTube Music. The Top Songs chart is only returned when authenticated with a premium account. :return: Dictionary containing new album releases, top songs (if authenticated with a premium account), moods & genres, popular episodes, trending tracks, and new music videos. Example:: { "new_releases": [ { "title": "Hangang", "type": "Album", "artists": [ { "id": "UCpo4SbqmPXpCVA5RFj-Gq5Q", "name": "Dept" } ], "browseId": "MPREb_rGl39ZNEl95", "audioPlaylistId": "OLAK5uy_mTZAp8a-agh1at-cVUGrwPhTJoM5GnKTk", "thumbnails": [...], "isExplicit": false } ], "top_songs": { "playlist": "VLPL4fGSI1pDJn6O1LS0XSdF3RyO0Rq_LDeI", "items": [ { "title": "Outside (Better Days)", "videoId": "oT79YlRtXDg", "playlistId": "VLPL4fGSI1pDJn6O1LS0XSdF3RyO0Rq_LDeI", "videoType": "MUSIC_VIDEO_TYPE_ATV", "artists": [ { "name": "MO3", "id": "UCdFt4Cvhr7Okaxo6hZg5K8g" }, { "name": "OG Bobby Billions", "id": "UCLusb4T2tW3gOpJS1fJ-A9g" } ], "thumbnails": [...], "isExplicit": true, "album": { "name": "Outside (Better Days)", "id": "MPREb_fX4Yv8frUNv" }, "rank": "1", "trend": "up" } ] }, "moods_and_genres": [ { "title": "Chill", "params": "ggMPOg1uXzVuc0dnZlhpV3Ba" } ], "top_episodes": [ { "title": "132. Lean Into Failure: How to Make Mistakes That Work | Think Fast, Talk Smart: Communication...", "description": "...", "duration": "25 min", "videoId": "xAEGaW2my7E", "browseId": "MPEDxAEGaW2my7E", "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE", "date": "Mar 5, 2024", "thumbnails": [...], "podcast": { "id": "PLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9", "name: "Stanford Graduate School of Business" } } ], "trending": { "playlist": "VLOLAK5uy_kNWGJvgWVqlt5LsFDL9Sdluly4M8TvGkM", "items": [ { "title": "Permission to Dance", "videoId": "CuklIb9d3fI", "videoType": "MUSIC_VIDEO_TYPE_OMV", "playlistId": "OLAK5uy_kNWGJvgWVqlt5LsFDL9Sdluly4M8TvGkM", "artists": [ { "name": "BTS", "id": "UC9vrvNSL3xcWGSkV86REBSg" } ], "thumbnails": [...], "isExplicit": false, "views": "108M" }, { "title": "Stanford GSB Podcasts", "podcast": { "name": "Stanford GSB Podcasts", "id": "PLxq_lXOUlvQDUNyoBYLkN8aVt5yAwEtG9" }, "browseId": "MPEDxAEGaW2my7E", "videoId": "xAEGaW2my7E", "videoType": "MUSIC_VIDEO_TYPE_PODCAST_EPISODE", "playlistId": "OLAK5uy_kNWGJvgWVqlt5LsFDL9Sdluly4M8TvGkM", "date": "Mar 5, 2024", "thumbnails": [...] } ] }, "new_videos": [ { "title": "EVERY CHANCE I GET (Official Music Video) (feat. Lil Baby & Lil Durk)", "videoId": "BTivsHlVcGU", "artists": [ { "name": "DJ Khaled", "id": "UC0Kgvj5t_c9EMWpEDWJuR1Q" } ], "playlistId": null, "thumbnails": [...], "views": "46M" } ] }

## Search Module
Responsible for handling `search` related actions.

### `search`
- **Endpoint:** `search`
- **Requires Authentication:** No
- **Description:** Search YouTube music Returns results within the provided category. :param query: Query string, i.e. 'Oasis Wonderwall' :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``community_playlists``, ``featured_playlists``, ``profiles``, ``podcasts``, ``episodes``. Default: Default search, including all types of items. :param scope: Search scope. Allowed values: ``library``, ``uploads``. Default: Search the public YouTube Music catalogue. Changing scope from the default will reduce the number of settable filters. Setting a filter that is not permitted will throw an exception. For uploads, no filter can be set. For library, community_playlists and featured_playlists filter cannot be set. :param limit: Number of search results to return Default: 20 :param ignore_spelling: Whether to ignore YTM spelling suggestions. If True, the exact search term will be searched for, and will not be corrected. This does not have any effect when the filter is set to ``uploads``. Default: False, will use YTM's default behavior of autocorrecting the search. :return: List of results depending on filter. resultType specifies the type of item (important for default search). albums, artists and playlists additionally contain a browseId, corresponding to albumId, channelId and playlistId (browseId=`VL`+playlistId) Example list for default search with one result per resultType for brevity. Normally there are 3 results per resultType and an additional ``thumbnails`` key:: [ { "category": "Top result", "resultType": "video", "videoId": "vU05Eksc_iM", "title": "Wonderwall", "artists": [ { "name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA" } ], "views": "1.4M", "videoType": "MUSIC_VIDEO_TYPE_OMV", "duration": "4:38", "duration_seconds": 278 }, { "category": "Songs", "resultType": "song", "videoId": "ZrOKjDZOtkA", "title": "Wonderwall", "artists": [ { "name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA" } ], "album": { "name": "(What's The Story) Morning Glory? (Remastered)", "id": "MPREb_9nqEki4ZDpp" }, "duration": "4:19", "duration_seconds": 259 "isExplicit": false, "inLibrary": false, "feedbackTokens": { "add": null, "remove": null }, "pinnedToListenAgain": false, "listenAgainFeedbackTokens": { "pin": null, "unpin": null } }, { "category": "Albums", "resultType": "album", "browseId": "MPREb_IInSY5QXXrW", "playlistId": "OLAK5uy_kunInnOpcKECWIBQGB0Qj6ZjquxDvfckg", "title": "(What's The Story) Morning Glory?", "type": "Album", "artist": "Oasis", "year": "1995", "isExplicit": false }, { "category": "Community playlists", "resultType": "playlist", "browseId": "VLPLK1PkWQlWtnNfovRdGWpKffO1Wdi2kvDx", "title": "Wonderwall - Oasis", "author": "Tate Henderson", "itemCount": "174" } itemCount of a playlist can be None as youtube music does not expose that information for search filtered to community playlist. , { "category": "Videos", "resultType": "video", "videoId": "bx1Bh8ZvH84", "title": "Wonderwall", "artists": [ { "name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA" } ], "views": "386M", "duration": "4:38", "duration_seconds": 278 }, { "category": "Artists", "resultType": "artist", "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA", "artist": "Oasis", "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg", "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg" }, { "category": "Profiles", "resultType": "profile", "title": "Taylor Swift Time", "name": "@TaylorSwiftTime", "browseId": "UCSCRK7XlVQ6fBdEl00kX6pQ", "thumbnails": ... } ]
- **Typical Payload Keys:** `query`

### `get_search_suggestions`
- **Endpoint:** `music/get_search_suggestions`
- **Requires Authentication:** No
- **Description:** Get Search Suggestions :param query: Query string, i.e. 'faded' :param detailed_runs: Whether to return detailed runs of each suggestion. If True, it returns the query that the user typed and the remaining suggestion along with the complete text (like many search services usually bold the text typed by the user). Default: False, returns the list of search suggestions in plain text. :return: A list of search suggestions. If ``detailed_runs`` is False, it returns plain text suggestions. If ``detailed_runs`` is True, it returns a list of dictionaries with detailed information. Example response when ``query`` is 'fade' and ``detailed_runs`` is set to ``False``:: [ "faded", "faded alan walker lyrics", "faded alan walker", "faded remix", "faded song", "faded lyrics", "faded instrumental" ] Example response when ``detailed_runs`` is set to ``True``:: [ { "text": "faded", "runs": [ { "text": "fade", "bold": true }, { "text": "d" } ], "fromHistory": true, "feedbackToken": "AEEJK..." }, { "text": "faded alan walker lyrics", "runs": [ { "text": "fade", "bold": true }, { "text": "d alan walker lyrics" } ], "fromHistory": false, "feedbackToken": None }, { "text": "faded alan walker", "runs": [ { "text": "fade", "bold": true }, { "text": "d alan walker" } ], "fromHistory": false, "feedbackToken": None }, ... ]
- **Typical Payload Keys:** `input`

### `remove_search_suggestions`
- **Endpoint:** `feedback`
- **Requires Authentication:** No
- **Description:** Remove search suggestion from the user search history. :param suggestions: The dictionary obtained from the :py:func:`get_search_suggestions` (with detailed_runs=True)` :param indices: Optional. The indices of the suggestions to be removed. Default: remove all suggestions. :return: True if the operation was successful, False otherwise. Example usage:: # Removing suggestion number 0 suggestions = ytmusic.get_search_suggestions(query="fade", detailed_runs=True) success = ytmusic.remove_search_suggestions(suggestions=suggestions, indices=[0]) if success: print("Suggestion removed successfully") else: print("Failed to remove suggestion")
- **Typical Payload Keys:** `feedbackTokens`
