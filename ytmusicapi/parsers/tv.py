"""
Parsers for responses of YouTube's TV client (``TVHTML5``).

OAuth tokens are only accepted by this client, see #813. Its responses contain less
information than the YouTube Music web client: there is no album, like status or
feedback token data, so the parsed results are a subset of the regular ones.
"""

import re

from ytmusicapi.continuations import get_continuation_string, get_continuations
from ytmusicapi.navigation import nav
from ytmusicapi.type_alias import JsonDict, JsonList, RequestFuncType

from ._utils import parse_duration

TV_SURFACE = ["contents", "tvBrowseRenderer", "content", "tvSurfaceContentRenderer", "content"]
TV_NAV_TABS = [
    "contents",
    "tvBrowseRenderer",
    "content",
    "tvSecondaryNavRenderer",
    "sections",
    0,
    "tvSecondaryNavSectionRenderer",
    "tabs",
]
TV_TILE = "tileRenderer"
TV_LOCKUP = "lockupViewModel"
TV_SEPARATOR = "•"

_LOCKUP_RESULT_TYPES = {
    "LOCKUP_CONTENT_TYPE_MUSIC": "song",
    "LOCKUP_CONTENT_TYPE_VIDEO": "video",
    "LOCKUP_CONTENT_TYPE_PLAYLIST": "playlist",
    "LOCKUP_CONTENT_TYPE_CHANNEL": "artist",
}
_PRIVACY_ICONS = {"PRIVACY_PRIVATE": "PRIVATE", "PRIVACY_UNLISTED": "UNLISTED", "PRIVACY_PUBLIC": "PUBLIC"}


def tv_text(node: JsonDict | None) -> str | None:
    """Get the text of a TV text node, which is either ``simpleText``, ``runs`` or ``content``"""
    if not node:
        return None
    if "simpleText" in node:
        return str(node["simpleText"])
    if "runs" in node:
        return "".join(run["text"] for run in node["runs"])
    if "content" in node:
        return str(node["content"])
    return None


def parse_tv_lines(lines: JsonList) -> list[list[JsonDict]]:
    """Returns the text nodes of each ``lineRenderer``, without separators and badges"""
    result = []
    for line in lines:
        texts = [
            nav(item, ["lineItemRenderer", "text"], True) for item in nav(line, ["lineRenderer", "items"])
        ]
        result.append([text for text in texts if text and tv_text(text) != TV_SEPARATOR])
    return result


def parse_tv_artists(text: JsonDict | None) -> JsonList:
    """Parse the artist/channel line of a tile. Ids are only available if the line consists of runs."""
    if not text:
        return []
    if "runs" in text:
        return [
            {"name": run["text"], "id": nav(run, ["navigationEndpoint", "browseEndpoint", "browseId"], True)}
            for run in text["runs"]
            if run["text"].strip(" ,&") and run["text"].strip() != TV_SEPARATOR
        ]
    return [{"name": tv_text(text), "id": None}]


def parse_tv_count(text: str | None) -> int | None:
    """Parse the item count from a text like ``Playlist • 35 tracks``"""
    if not text:
        return None
    for part in reversed(text.split(TV_SEPARATOR)):
        if match := re.match(r"^\s*(\d[\d,.]*)\s+\D+$", part):
            return int(re.sub(r"\D", "", match.group(1)))
    return None


def get_tv_tab_contents(response: JsonDict, renderer: str = "gridRenderer") -> JsonDict | None:
    """Get the contents of the selected tab on a tabbed TV page, i.e. the library"""
    for tab in nav(response, TV_NAV_TABS, True) or []:
        if nav(tab, ["tabRenderer", "selected"], True):
            return nav(tab, ["tabRenderer", "content", "tvSurfaceContentRenderer", "content", renderer], True)
    return None


def parse_tv_playlist_tile(data: JsonDict) -> JsonDict:
    """Parse a playlist (or album) tile, i.e. from the library"""
    metadata = nav(data, ["metadata", "tileMetadataRenderer"])
    lines = [[tv_text(text) for text in line] for line in parse_tv_lines(metadata.get("lines", []))]
    browse_id = nav(data, ["onSelectCommand", "browseEndpoint", "browseId"], True) or ""
    description = f" {TV_SEPARATOR} ".join(text for line in lines for text in line if text)
    playlist: JsonDict = {
        "title": tv_text(metadata["title"]),
        "playlistId": browse_id.removeprefix("VL"),
        "thumbnails": nav(data, ["header", "tileHeaderRenderer", "thumbnail", "thumbnails"], True),
        "description": description,
        "count": parse_tv_count(description),
    }
    # two lines: author, description. one line: "Auto playlist • author • count"
    if len(lines) > 1 and lines[0]:
        playlist["author"] = [{"name": lines[0][0], "id": None}]
    return playlist


def parse_tv_playlist_tiles(results: JsonList) -> JsonList:
    return [
        parse_tv_playlist_tile(result[TV_TILE])
        for result in results
        if nav(result, [TV_TILE, "onSelectCommand", "browseEndpoint"], True)
    ]


def parse_tv_library_playlists(
    response: JsonDict, request_func: RequestFuncType, limit: int | None
) -> JsonList:
    results = get_tv_tab_contents(response)
    if results is None:
        return []
    playlists = parse_tv_playlist_tiles(results.get("items", []))
    if "continuations" in results:
        remaining_limit = None if limit is None else (limit - len(playlists))
        playlists.extend(
            get_continuations(
                results, "gridContinuation", remaining_limit, request_func, parse_tv_playlist_tiles
            )
        )
    return playlists


def parse_tv_playlist_item(data: JsonDict) -> JsonDict:
    """Parse a track tile of a playlist"""
    # tracks of albums only have a header with title and duration
    track_header = nav(data, ["header", "trackTileHeaderRenderer"], True)
    metadata = nav(data, ["metadata", "tileMetadataRenderer"], True) or track_header or {}
    lines = parse_tv_lines(metadata.get("lines", []))
    duration = tv_text(
        track_header.get("duration")
        if track_header
        else nav(
            data,
            [
                "header",
                "tileHeaderRenderer",
                "thumbnailOverlays",
                0,
                "thumbnailOverlayTimeStatusRenderer",
                "text",
            ],
            True,
        )
    )
    header = track_header or nav(data, ["header", "tileHeaderRenderer"], True) or {}
    track: JsonDict = {
        "videoId": nav(data, ["onSelectCommand", "watchEndpoint", "videoId"], True) or data.get("contentId"),
        "title": tv_text(metadata.get("title")),
        "artists": parse_tv_artists(lines[0][0] if lines and lines[0] else None),
        "album": None,
        "thumbnails": nav(header, ["thumbnail", "thumbnails"], True),
        "isAvailable": "onSelectCommand" in data,
        "videoType": nav(
            metadata,
            [
                "title",
                "runs",
                0,
                "navigationEndpoint",
                "watchEndpoint",
                "watchEndpointMusicSupportedConfigs",
                "watchEndpointMusicConfig",
                "musicVideoType",
            ],
            True,
        ),
    }
    if duration:
        track["duration"] = duration
        track["duration_seconds"] = parse_duration(duration)

    # the "Remove from playlist" menu item of owned playlists holds the setVideoId
    for item in (
        nav(data, ["onLongPressCommand", "showMenuCommand", "menu", "menuRenderer", "items"], True) or []
    ):
        for action in (
            nav(item, ["menuServiceItemRenderer", "serviceEndpoint", "playlistEditEndpoint", "actions"], True)
            or []
        ):
            if "setVideoId" in action:
                track["setVideoId"] = action["setVideoId"]
    return track


def parse_tv_playlist_items(results: JsonList) -> JsonList:
    return [parse_tv_playlist_item(result[TV_TILE]) for result in results if TV_TILE in result]


TV_DESCRIPTION_POPUP = [
    "buttonRenderer",
    "command",
    "openPopupAction",
    "popup",
    "overlaySectionRenderer",
    "overlay",
    "overlayTwoPanelRenderer",
    "actionPanel",
    "overlayPanelRenderer",
    "content",
    "scrollPaneRenderer",
    "content",
    "scrollPaneItemListRenderer",
    "items",
    0,
    "overlayMessageRenderer",
    "subtitle",
]


def parse_tv_playlist_description(header: JsonDict) -> str | None:
    """The description of a playlist is only part of a popup, which is opened by one of the header buttons"""
    for button in header.get("buttons", []):
        if description := tv_text(nav(button, TV_DESCRIPTION_POPUP, True)):
            return description
    return None


def parse_tv_playlist(response: JsonDict, request_func: RequestFuncType, limit: int | None) -> JsonDict:
    columns = nav(response, [*TV_SURFACE, "twoColumnRenderer"])
    header = nav(columns, ["leftColumn", "entityMetadataRenderer"])
    results = nav(columns, ["rightColumn", "playlistVideoListRenderer"])

    playlist: JsonDict = {
        "id": results["playlistId"],
        "owned": results.get("isEditable", False),
        "privacy": "PUBLIC",
        "title": tv_text(header.get("title")),
        "description": tv_text(header.get("description")) or parse_tv_playlist_description(header),
        "thumbnails": nav(header, ["thumbnail", "thumbnails"], True),
        "author": None,
        "trackCount": None,
        "related": [],
    }
    for line in header.get("bylines", []):
        texts = []
        for item in nav(line, ["lineRenderer", "items"]):
            item = item["lineItemRenderer"]
            icon = nav(item, ["badge", "metadataBadgeRenderer", "icon", "iconType"], True)
            if icon in _PRIVACY_ICONS:
                playlist["privacy"] = _PRIVACY_ICONS[icon]
            text = tv_text(item.get("text"))
            if text and text != TV_SEPARATOR:
                texts.append(text)
        # the author is the item before the track count: "[Auto playlist •] author • 3 videos [• year or views]"
        for i, text in enumerate(texts):
            if playlist["trackCount"] is None and (count := parse_tv_count(text)) is not None:
                playlist["trackCount"] = count
                if i > 0:
                    playlist["author"] = {"name": texts[i - 1], "id": None}
            elif re.fullmatch(r"\d{4}", text):
                playlist["year"] = text

    playlist["tracks"] = parse_tv_playlist_items(results.get("contents", []))
    if "continuations" in results:
        remaining_limit = None if limit is None else (limit - len(playlist["tracks"]))
        playlist["tracks"].extend(
            get_continuations(
                results,
                "playlistVideoListContinuation",
                remaining_limit,
                request_func,
                parse_tv_playlist_items,
            )
        )
    if limit is not None:
        playlist["tracks"] = playlist["tracks"][:limit]
    return playlist


def parse_tv_search_result(data: JsonDict, category: str | None) -> JsonDict | None:
    """Parse a search result. Returns None for result types that are not music related (Shorts)"""
    result_type = _LOCKUP_RESULT_TYPES.get(data.get("contentType", ""))
    if result_type is None:
        return None

    metadata = nav(data, ["metadata", "lockupMetadataViewModel"])
    rows = [
        [text for part in row.get("metadataParts", []) if (text := nav(part, ["text", "content"], True))]
        for row in nav(metadata, ["metadata", "contentMetadataViewModel", "metadataRows"], True) or []
    ]
    image = data.get("contentImage", {})
    thumbnail = nav(image, ["collectionThumbnailViewModel", "primaryThumbnail"], True) or image
    thumbnail = thumbnail.get("thumbnailViewModel", {})
    content_id = data["contentId"]
    result: JsonDict = {
        "category": category,
        "resultType": result_type,
        "title": tv_text(metadata.get("title")),
        "thumbnails": nav(thumbnail, ["image", "sources"], True),
    }
    byline = rows[0][0] if rows and rows[0] else None

    if result_type in ("song", "video"):
        result["videoId"] = content_id
        result["artists"] = [{"name": byline, "id": None}] if byline else []
        result["views"] = rows[1][0].split(" ")[0] if len(rows) > 1 and rows[1] else None
        for overlay in thumbnail.get("overlays", []):
            for badge in nav(overlay, ["thumbnailBottomOverlayViewModel", "badges"], True) or []:
                duration = nav(badge, ["thumbnailBadgeViewModel", "text"], True)
                if duration and parse_duration(duration) is not None:
                    result["duration"] = duration
                    result["duration_seconds"] = parse_duration(duration)
    elif result_type == "playlist":
        # albums are audio playlists on the TV client, they can be retrieved with get_playlist
        if content_id.startswith("OLAK"):
            result["resultType"] = "album"
            result["artists"] = [{"name": byline, "id": None}] if byline else []
        else:
            result["author"] = byline
        result["playlistId"] = content_id
        result["browseId"] = "VL" + content_id
    else:
        result["artist"] = result["title"]
        result["browseId"] = content_id
        result["subscribers"] = rows[-1][0].split(" ")[0] if len(rows) > 1 and rows[-1] else None
    return result


def parse_tv_search_results(results: JsonList, category: str | None) -> JsonList:
    parsed = [
        parse_tv_search_result(result[TV_LOCKUP], category) for result in results if TV_LOCKUP in result
    ]
    return [result for result in parsed if result is not None]


def parse_tv_album_tile(data: JsonDict) -> JsonDict:
    """Parse an album tile. Albums are audio playlists on the TV client and can be retrieved with get_playlist"""
    playlist = parse_tv_playlist_tile(data)
    metadata = nav(data, ["metadata", "tileMetadataRenderer"])
    lines = parse_tv_lines(metadata.get("lines", []))
    subtitle = [part.strip() for part in (playlist["description"] or "").split(TV_SEPARATOR)]
    year = next((part for part in subtitle if re.fullmatch(r"\d{4}", part)), None)
    return {
        "browseId": None,
        "playlistId": playlist["playlistId"],
        "title": playlist["title"],
        "type": tv_text(lines[1][0]).split(TV_SEPARATOR)[0].strip() if len(lines) > 1 and lines[1] else None,  # type: ignore[union-attr]
        "year": year,
        "artists": parse_tv_artists(lines[0][0] if lines and lines[0] else None),
        "thumbnails": playlist["thumbnails"],
    }


def parse_tv_channel_tile(data: JsonDict) -> JsonDict:
    """Parse an artist/channel tile. Library subscriptions only contain the id of the artist's radio."""
    metadata = nav(data, ["metadata", "tileMetadataRenderer"])
    content_id = data.get("contentId") or ""
    browse_id = nav(data, ["onSelectCommand", "browseEndpoint", "browseId"], True)
    return {
        "artist": tv_text(metadata["title"]),
        "browseId": browse_id or (content_id if content_id.startswith("UC") else None),
        "radioId": nav(data, ["onSelectCommand", "watchPlaylistEndpoint", "playlistId"], True),
        "thumbnails": nav(data, ["header", "tileHeaderRenderer", "thumbnail", "thumbnails"], True),
    }


def parse_tv_tile(data: JsonDict) -> JsonDict | None:
    """Parse any tile based on its content type. Returns None for unsupported types (Shorts)"""
    match data.get("contentType"):
        case "TILE_CONTENT_TYPE_VIDEO":
            return parse_tv_playlist_item(data)
        case "TILE_CONTENT_TYPE_PLAYLIST":
            browse_id = nav(data, ["onSelectCommand", "browseEndpoint", "browseId"], True) or ""
            return (
                parse_tv_album_tile(data) if browse_id.startswith("VLOLAK") else parse_tv_playlist_tile(data)
            )
        case "TILE_CONTENT_TYPE_CHANNEL":
            return parse_tv_channel_tile(data)
    return None


def parse_tv_tiles(results: JsonList) -> JsonList:
    # tiles without metadata are navigation links, i.e. to related channels
    parsed = [parse_tv_tile(result[TV_TILE]) for result in results if "metadata" in result.get(TV_TILE, {})]
    return [result for result in parsed if result is not None]


def parse_tv_library_tab(response: JsonDict, request_func: RequestFuncType, limit: int | None) -> JsonList:
    """Parse the selected tab of the library (albums, songs, subscriptions) including continuations"""
    results = get_tv_tab_contents(response)
    if results is None:
        return []
    items = parse_tv_tiles(results.get("items", []))
    if "continuations" in results:
        remaining_limit = None if limit is None else (limit - len(items))
        items.extend(
            get_continuations(results, "gridContinuation", remaining_limit, request_func, parse_tv_tiles)
        )
    return items if limit is None else items[:limit]


def parse_tv_artist(response: JsonDict) -> JsonDict:
    surface = nav(response, TV_SURFACE[:-1])
    header = nav(surface, ["header", "channelHeaderRenderer"])
    subtitle = [tv_text(text) for line in parse_tv_lines([header["subtitle"]]) for text in line]
    artist: JsonDict = {
        "name": tv_text(header.get("title")),
        "channelId": None,
        "description": tv_text(
            nav(header, ["selectableDescription", "selectableTextRenderer", "text"], True)
        ),
        "subscribers": subtitle[-1].split(" ")[0] if len(subtitle) > 1 and subtitle[-1] else None,
        "subscribed": None,
        "shuffleId": None,
        "radioId": None,
        "thumbnails": nav(header, ["avatar", "thumbnails"], True),
        "sections": [],
    }
    for button in header.get("buttons", []):
        if subscribe := button.get("subscribeButtonRenderer"):
            artist["channelId"] = subscribe.get("channelId")
            artist["subscribed"] = subscribe.get("subscribed")
        playlist_id = nav(
            button, ["buttonRenderer", "navigationEndpoint", "watchPlaylistEndpoint", "playlistId"], True
        )
        icon = nav(button, ["buttonRenderer", "icon", "iconType"], True)
        if playlist_id and icon == "SHUFFLE":
            artist["shuffleId"] = playlist_id
        elif playlist_id and icon == "MIX":
            artist["radioId"] = playlist_id

    for section in nav(surface, ["content", *["sectionListRenderer", "contents"]], True) or []:
        shelf = section.get("shelfRenderer", {})
        contents = parse_tv_tiles(nav(shelf, ["content", "horizontalListRenderer", "items"], True) or [])
        if not contents:
            continue
        header_renderer = nav(shelf, ["headerRenderer", "shelfHeaderRenderer"], True) or {}
        title = nav(
            header_renderer, ["avatarLockup", "avatarLockupRenderer", "title"], True
        ) or header_renderer.get("title")
        artist["sections"].append(
            {
                "title": tv_text(title),
                "browseId": nav(title, ["runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"], True),
                "contents": contents,
            }
        )
    return artist


def parse_tv_watch_playlist_items(results: JsonList) -> JsonList:
    """Parse the "Up next" items of the watch page into the format of ``get_watch_playlist``"""
    tracks = []
    for result in results:
        data = nav(
            result, ["playlistPanelVideoWrapperRenderer", "primaryRenderer", TV_TILE], True
        ) or result.get(TV_TILE)
        if not data or "onSelectCommand" not in data:
            continue
        track = parse_tv_playlist_item(data)
        track["length"] = track.pop("duration", None)
        track.pop("duration_seconds", None)
        track["thumbnail"] = track.pop("thumbnails")
        track["likeStatus"] = None
        lines = parse_tv_lines(nav(data, ["metadata", "tileMetadataRenderer", "lines"], True) or [])
        year = tv_text(lines[1][0]) if len(lines) > 1 and lines[1] else None
        track["year"] = year if year and re.fullmatch(r"\d{4}", year) else None
        tracks.append(track)
    return tracks


def parse_tv_watch_playlist(response: JsonDict, request_func: RequestFuncType, limit: int) -> JsonDict:
    watch_next = nav(response, ["contents", "singleColumnWatchNextResults"])
    playlist_id = nav(watch_next, ["playlist", "playlist", "playlistId"], True)
    tracks: JsonList = []
    # with a playlist, the first shelf is the queue ("Up next"). The other shelves are recommendations
    results = nav(
        watch_next,
        ["pivot", "sectionListRenderer", "contents", 0, "shelfRenderer", "content", "horizontalListRenderer"],
        True,
    )
    if playlist_id and results:
        tracks = parse_tv_watch_playlist_items(results.get("items", []))
        while len(tracks) < limit:
            # continuation lists may also contain previous and reload continuations
            ctoken = next(
                (
                    data["continuation"]
                    for continuation in results.get("continuations", [])
                    for key, data in continuation.items()
                    if key in ("nextContinuationData", "nextRadioContinuationData")
                ),
                None,
            )
            if not ctoken:
                break
            continuation = request_func(get_continuation_string(ctoken))
            results = nav(continuation, ["continuationContents", "horizontalListContinuation"], True)
            if not results or not (contents := parse_tv_watch_playlist_items(results.get("items", []))):
                break
            tracks.extend(contents)
    return {"tracks": tracks, "playlistId": playlist_id, "lyrics": None, "related": None}
