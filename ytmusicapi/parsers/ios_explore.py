"""
iOS-specific parsers for ytmusicapi

This module contains parsers specifically designed to handle iOS YouTube Music API responses
that have different structure from desktop responses.
"""

from ytmusicapi.navigation import (
    NAVIGATION_BROWSE_ID,
    THUMBNAIL_RENDERER,
    TITLE_TEXT,
    nav,
)
from ytmusicapi.type_alias import JsonDict


def parse_chart_playlist_ios(data: JsonDict) -> JsonDict:
    """
    iOS-specific parser for chart playlists.
    
    In iOS responses, the navigationEndpoint is at the top level of the item,
    not inside the title runs like in desktop responses.
    """
    return {
        "title": nav(data, TITLE_TEXT),
        "playlistId": nav(data, NAVIGATION_BROWSE_ID)[2:],  # Remove "VL" prefix
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }


def parse_chart_artist_ios(data: JsonDict) -> JsonDict:
    """
    iOS-specific parser for chart artists.
    This may need adjustments based on iOS response structure.
    """
    # For now, use the same logic as desktop - may need adjustment
    from ytmusicapi.parsers.explore import parse_chart_artist
    return parse_chart_artist(data)
