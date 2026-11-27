"""
Parsers for responses of the official YouTube Data API v3.

With OAuth authentication, the Data API is used where it is available, as it is complete and stable.
YouTube's TV client is only used for what the Data API does not offer, see #813.
"""

import base64
import binascii
import re

from ytmusicapi.type_alias import JsonDict, JsonList

_UNAVAILABLE_TITLES = ("Deleted video", "Private video")


def parse_data_api_set_video_id(playlist_item_id: str) -> str | None:
    """
    The id of a playlist item is the base64 encoded ``<playlistId>.<setVideoId>``.
    The setVideoId is needed to move or remove playlist items with :py:func:`edit_playlist`
    and :py:func:`remove_playlist_items`.
    """
    try:
        padded = playlist_item_id + "=" * (-len(playlist_item_id) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None
    set_video_id = decoded.rpartition(".")[2]
    return set_video_id if re.fullmatch(r"[0-9A-F]{16}", set_video_id) else None


def parse_data_api_duration(duration: str | None) -> int | None:
    """Parse an ISO 8601 duration like ``PT1H4M40S`` to seconds"""
    match = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match or not any(match.groups()):
        return None
    days, hours, minutes, seconds = (int(group or 0) for group in match.groups())
    return ((days * 24 + hours) * 60 + minutes) * 60 + seconds


def format_duration(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"


def parse_data_api_thumbnails(thumbnails: JsonDict | None) -> JsonList:
    return sorted((thumbnails or {}).values(), key=lambda thumbnail: thumbnail.get("width", 0))


def parse_data_api_playlist_items(items: JsonList, videos: JsonList) -> JsonList:
    """
    :param items: ``playlistItems`` resources with the parts ``snippet``, ``contentDetails`` and ``status``
    :param videos: ``videos`` resources of the items with the part ``contentDetails``, for the duration
    """
    durations = {video["id"]: video["contentDetails"].get("duration") for video in videos}
    tracks = []
    for item in items:
        snippet = item["snippet"]
        video_id = item["contentDetails"]["videoId"]
        artist = snippet.get("videoOwnerChannelTitle")
        track: JsonDict = {
            "videoId": video_id,
            "title": snippet.get("title"),
            # channels of songs are auto-generated and named "<artist> - Topic"
            "artists": [{"name": artist.removesuffix(" - Topic"), "id": snippet.get("videoOwnerChannelId")}]
            if artist
            else [],
            "album": None,
            "thumbnails": parse_data_api_thumbnails(snippet.get("thumbnails")),
            "isAvailable": video_id in durations and snippet.get("title") not in _UNAVAILABLE_TITLES,
            "videoType": None,
        }
        if (duration_seconds := parse_data_api_duration(durations.get(video_id))) is not None:
            track["duration"] = format_duration(duration_seconds)
            track["duration_seconds"] = duration_seconds
        if set_video_id := parse_data_api_set_video_id(item["id"]):
            track["setVideoId"] = set_video_id
        tracks.append(track)
    return tracks


def parse_data_api_playlist(playlist_id: str, header: JsonDict | None, channel_id: str | None) -> JsonDict:
    """
    :param header: ``playlists`` resource with the parts ``snippet``, ``contentDetails`` and ``status``.
        Not available for some playlists, i.e. liked songs.
    :param channel_id: channel id of the authenticated user
    """
    snippet = (header or {}).get("snippet", {})
    return {
        "id": playlist_id,
        "owned": bool(channel_id) and snippet.get("channelId") == channel_id,
        "privacy": (header or {}).get("status", {}).get("privacyStatus", "public").upper(),
        "title": snippet.get("title"),
        "description": snippet.get("description") or None,
        "thumbnails": parse_data_api_thumbnails(snippet.get("thumbnails")),
        "author": {"name": snippet["channelTitle"], "id": snippet.get("channelId")}
        if snippet.get("channelTitle")
        else None,
        "trackCount": (header or {}).get("contentDetails", {}).get("itemCount"),
        "related": [],
    }
