from dataclasses import dataclass
from typing import Any

from ytmusicapi.type_alias import JsonDict, JsonList

from .songs import *

PROGRESS_RENDERER = ["musicPlaybackProgressRenderer"]
DURATION_TEXT = ["durationText", "runs", 1, "text"]


@dataclass
class DescriptionElement:
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass
class Link(DescriptionElement):
    url: str


@dataclass
class Timestamp(DescriptionElement):
    seconds: int


@dataclass
class Description(list[DescriptionElement]):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(args[0])

    @property
    def text(self) -> str:
        return "".join(str(element) for element in self)

    @classmethod
    def from_runs(cls, description_runs: JsonList) -> "Description":
        """parse the description runs into a usable format

        :param description_runs: the original description runs

        :return: List of text (str), timestamp (int) and link values (Link object)
        """
        elements: list[DescriptionElement] = []
        for run in description_runs:
            navigationEndpoint = nav(run, ["navigationEndpoint"], True)
            if navigationEndpoint:
                element = DescriptionElement("")
                if "urlEndpoint" in navigationEndpoint:
                    element = Link(text=run["text"], url=navigationEndpoint["urlEndpoint"]["url"])
                elif "watchEndpoint" in navigationEndpoint:
                    element = Timestamp(
                        text=run["text"],
                        seconds=nav(navigationEndpoint, ["watchEndpoint", "startTimeSeconds"]),
                    )
            else:
                element = DescriptionElement(text=nav(run, ["text"], True))  # type: ignore

            elements.append(element)

        return cls(elements)


def parse_base_header(header: JsonDict) -> JsonDict:
    """parse common left hand side (header) items of an episode or podcast page"""
    strapline = nav(header, ["straplineTextOne"])

    author = {
        "name": nav(strapline, [*RUN_TEXT], True),
        "id": nav(strapline, ["runs", 0, *NAVIGATION_BROWSE_ID], True),
    }

    return {
        "author": author if author["name"] else None,
        "title": nav(header, TITLE_TEXT),
        "thumbnails": nav(header, THUMBNAILS),
    }


def parse_podcast_header(header: JsonDict) -> JsonDict:
    metadata = parse_base_header(header)
    metadata["description"] = nav(header, ["description", *DESCRIPTION_SHELF, *DESCRIPTION], True)
    metadata["saved"] = nav(header, ["buttons", 1, *TOGGLED_BUTTON])

    return metadata


def parse_episode_header(header: JsonDict) -> JsonDict:
    metadata = parse_base_header(header)
    metadata["date"] = nav(header, [*SUBTITLE])
    progress_renderer = nav(header, ["progress", *PROGRESS_RENDERER])
    metadata["duration"] = nav(progress_renderer, DURATION_TEXT, True)
    metadata["progressPercentage"] = nav(progress_renderer, ["playbackProgressPercentage"])
    metadata["saved"] = nav(header, ["buttons", 0, *TOGGLED_BUTTON], True) or False

    metadata["playlistId"] = None
    menu_buttons = nav(header, ["buttons", -1, "menuRenderer", "items"])
    for button in menu_buttons:
        if nav(button, [MNIR, *ICON_TYPE], True) == "BROADCAST":
            metadata["playlistId"] = nav(button, [MNIR, *NAVIGATION_BROWSE_ID])

    return metadata


def parse_episode(data: JsonDict) -> JsonDict:
    """Parses a single episode under "Episodes" on a channel page or on a podcast page"""
    thumbnails = nav(data, THUMBNAILS)
    date = nav(data, SUBTITLE, True)
    duration = nav(data, ["playbackProgress", *PROGRESS_RENDERER, *DURATION_TEXT], True)
    title = nav(data, TITLE_TEXT)
    description = nav(data, DESCRIPTION, True)
    videoId = nav(data, ["onTap", *WATCH_VIDEO_ID], True)
    browseId = nav(data, [*TITLE, *NAVIGATION_BROWSE_ID], True)
    videoType = nav(data, ["onTap", *NAVIGATION_VIDEO_TYPE], True)
    index = nav(data, ["onTap", "watchEndpoint", "index"], True)
    return {
        "index": index,
        "title": title,
        "description": description,
        "duration": duration,
        "videoId": videoId,
        "browseId": browseId,
        "videoType": videoType,
        "date": date,
        "thumbnails": thumbnails,
    }


def parse_podcast(data: JsonDict) -> JsonDict:
    """Parses a single podcast under "Podcasts" on a channel page"""
    return {
        "title": nav(data, TITLE_TEXT),
        "channel": parse_id_name(nav(data, [*SUBTITLE_RUNS, 0], True)),
        "browseId": nav(data, TITLE + NAVIGATION_BROWSE_ID),
        "podcastId": nav(data, THUMBNAIL_OVERLAY, True),
        "thumbnails": nav(data, THUMBNAIL_RENDERER),
    }
