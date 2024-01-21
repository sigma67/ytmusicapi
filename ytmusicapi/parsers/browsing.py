from ._utils import *
from .songs import *


def parse_mixed_content(rows):
    items = []
    for row in rows:
        if DESCRIPTION_SHELF[0] in row:
            results = nav(row, DESCRIPTION_SHELF)
            title = nav(results, ["header", *RUN_TEXT])
            contents = nav(results, DESCRIPTION)
        else:
            results = next(iter(row.values()))
            if "contents" not in results:
                continue
            title = nav(results, [*CAROUSEL_TITLE, "text"])
            contents = []
            for result in results["contents"]:
                data = nav(result, [MTRIR], True)
                content = None
                if data:
                    page_type = nav(data, TITLE + NAVIGATION_BROWSE + PAGE_TYPE, True)
                    if page_type is None:  # song or watch_playlist
                        if nav(data, NAVIGATION_WATCH_PLAYLIST_ID, True) is not None:
                            content = parse_watch_playlist(data)
                        else:
                            content = parse_song(data)
                    elif page_type == "MUSIC_PAGE_TYPE_ALBUM":
                        content = parse_album(data)
                    elif page_type == "MUSIC_PAGE_TYPE_ARTIST":
                        content = parse_related_artist(data)
                    elif page_type == "MUSIC_PAGE_TYPE_PLAYLIST":
                        content = parse_playlist(data)
                else:
                    data = nav(result, [MRLIR], True)
                    if not data:
                        continue
                    content = parse_song_flat(data)

                contents.append(content)

        items.append({"title": title, "contents": contents})
    return items


def parse_content_list(results, parse_func, key=MTRIR):
    contents = []
    for result in results:
        contents.append(parse_func(result[key]))

    return contents


def parse_album(result):
    album = {
        "title": nav(result, TITLE_TEXT),
        "browseId": nav(result, TITLE + NAVIGATION_BROWSE_ID),
        "audioPlaylistId": nav(result, THUMBNAIL_OVERLAY, True),
        "thumbnails": nav(result, THUMBNAIL_RENDERER),
        "isExplicit": nav(result, SUBTITLE_BADGE_LABEL, True) is not None,
    }

    runs = nav(result, SUBTITLE_RUNS)
    if len(runs) >= 2:
        album["type"] = nav(runs, ZTEXT, True)

        # navigationEndpoint key is present when secondary runs are artists
        if "navigationEndpoint" in runs[2]:
            album["artists"] = artists_from_runs(runs)
        else:
            album["year"] = nav(runs, TTEXT, True)

    # it's a single with just the year
    else:
        album["type"] = "Single"
        album["year"] = nav(runs, ZTEXT, True)

    return album


def parse_song(result):
    song = {
        "title": nav(result, TITLE_TEXT),
        "videoId": nav(result, NAVIGATION_VIDEO_ID),
        "playlistId": nav(result, NAVIGATION_PLAYLIST_ID, True),
        "thumbnails": nav(result, THUMBNAIL_RENDERER),
    }
    song.update(parse_song_runs(nav(result, SUBTITLE_RUNS)))
    return song


def parse_song_flat(data):
    columns = [get_flex_column_item(data, i) for i in range(0, len(data["flexColumns"]))]
    song = {
        "title": nav(columns[0], TEXT_RUN_TEXT),
        "videoId": nav(columns[0], TEXT_RUN + NAVIGATION_VIDEO_ID, True),
        "artists": parse_pl_song_artists(data, 1),
        "thumbnails": nav(data, THUMBNAILS),
        "isExplicit": nav(data, BADGE_LABEL, True) is not None,
    }
    if (
        len(columns) > 2
        and columns[2] is not None
        and "navigationEndpoint" in (targ := nav(columns[2], TEXT_RUN))
    ):
        song["album"] = parse_id_name(targ)
    else:
        song["views"] = nav(columns[1], ["text", "runs", -1, "text"]).split(" ")[0]

    return song


def parse_video(result):
    runs = nav(result, SUBTITLE_RUNS)
    # artists_len = get_dot_separator_index(runs)
    videoId = nav(result, NAVIGATION_VIDEO_ID, True)
    if not videoId:
        # I believe this
        videoId = next(
            (
                found
                for entry in nav(result, MENU_ITEMS)
                if (found := nav(entry, MENU_SERVICE + QUEUE_VIDEO_ID, True))
            ),
            None,
        )  # this won't match anything for episodes, None to catch iterator
    result = {
        "title": nav(result, TITLE_TEXT),
        "videoId": videoId,
        "playlistId": nav(result, NAVIGATION_PLAYLIST_ID, True),
        "thumbnails": nav(result, THUMBNAIL_RENDERER, True),
    }

    # it's an ~episode~ -> makes the first key a duration { "text": "%m min %s sec" } format
    # unsure if we should capture the duration for edge cases
    # could also be an unlinked artist
    if "navigationEndpoint" not in runs[0] and any(x in runs[0]["text"] for x in ["sec", "min"]):
        result["type"] = "episode"
        # views are unavailable on episodes
        result["views"] = None
        result["view_count"] = -1
        result["artists"] = artists_from_runs(runs[2:], 0)
    else:
        result["type"] = "song"
        result["views"] = runs[-1]["text"].split(" ")[0]
        result["view_count"] = parse_real_count(runs[-1]) if len(runs) > 2 else -1
        result["artists"] = artists_from_runs(runs[:-2], 0)

    return result


def parse_playlist(data):
    playlist = {
        "title": nav(data, TITLE_TEXT),
        "playlistId": nav(data, TITLE + NAVIGATION_BROWSE_ID)[2:],
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }
    runs = nav(data, SUBTITLE_RUNS)
    if runs:
        playlist["description"] = "".join([run["text"] for run in runs])
        if len(runs) == 3 and runs[1]["text"] == " • ":
            # genre charts from get_charts('US') are sent here...
            if runs[0]["text"] == "Chart" or runs[-1]["text"] == "YouTube Music":
                playlist["count"] = None
                playlist["view_count"] = -1
                playlist["author"] = {"name": "YouTube Music", "id": None}
                playlist["featured_artists"] = None
            else:
                playlist["count"] = nav(data, SUBTITLE2).split(" ")[0]  # this is "views" everywhere else
                playlist["view_count"] = parse_real_count(runs[2])
                playlist["author"] = parse_id_name(runs[0])
                playlist["featured_artists"] = None
        else:
            playlist["featured_artists"] = nav(runs, ZTEXT, True)
            # fill default, maintain return format
            playlist["author"] = {"name": "YouTube Music", "id": None}
            playlist["view_count"] = -1

    return playlist


def parse_related_artist(data):
    subscribers = nav(data, SUBTITLE, True)
    if subscribers:
        subscribers = subscribers.split(" ")[0]
    return {
        "title": nav(data, TITLE_TEXT),
        "browseId": nav(data, TITLE + NAVIGATION_BROWSE_ID),
        "subscribers": subscribers,
        "sub_count": parse_real_count(nav(data, LAST_SUB_RUN, True)),
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }


def parse_watch_playlist(data):
    return {
        "title": nav(data, TITLE_TEXT),
        "playlistId": nav(data, NAVIGATION_WATCH_PLAYLIST_ID),
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }
