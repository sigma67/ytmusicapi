import typing

from ytmusicapi.type_alias import JsonDict, JsonList

from .songs import *


def parse_watch_playlist(results: JsonList) -> JsonList:
    tracks = []
    PPVWR = "playlistPanelVideoWrapperRenderer"
    PPVR = "playlistPanelVideoRenderer"
    for result in results:
        counterpart = None
        if PPVWR in result:
            counterpart = result[PPVWR]["counterpart"][0]["counterpartRenderer"][PPVR]
            result = result[PPVWR]["primaryRenderer"]
        if PPVR not in result:
            continue
        data = result[PPVR]
        if "unplayableText" in data:
            continue

        track = parse_watch_track(data)
        if counterpart:
            track["counterpart"] = parse_watch_track(counterpart)
        tracks.append(track)

    return tracks


def parse_watch_track(data: JsonDict) -> JsonDict:
    like_status = None
    for item in nav(data, MENU_ITEMS):
        if TOGGLE_MENU in item:
            service = item[TOGGLE_MENU]["defaultServiceEndpoint"]
            if "likeEndpoint" in service:
                like_status = parse_like_status(service)

    track = {
        "videoId": data["videoId"],
        "title": nav(data, TITLE_TEXT),
        "length": nav(data, ["lengthText", "runs", 0, "text"], True),
        "thumbnail": nav(data, THUMBNAIL),
        "likeStatus": like_status,
        "videoType": nav(data, ["navigationEndpoint", *NAVIGATION_VIDEO_TYPE], True),
    }

    track.update(
        {
            "inLibrary": None,
            "feedbackTokens": None,
            "pinnedToListenAgain": None,
            "listenAgainFeedbackTokens": None,
        }
        | parse_song_menu_data(data)
    )

    if longBylineText := nav(data, ["longBylineText"]):
        song_info = parse_song_runs(longBylineText["runs"])
        track.update(song_info)

    return track


def get_tab_browse_id(watchNextRenderer: JsonDict, tab_id: int) -> str | None:
    if "unselectable" not in watchNextRenderer["tabs"][tab_id]["tabRenderer"]:
        return typing.cast(
            str, watchNextRenderer["tabs"][tab_id]["tabRenderer"]["endpoint"]["browseEndpoint"]["browseId"]
        )
    else:
        return None
