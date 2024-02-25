from dataclasses import dataclass
from typing import Sequence

from .songs import *


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
class Description(Sequence):
    def __len__(self):
        return len(self.elements)

    def __getitem__(self, index):
        return self.elements[index]

    elements: Sequence[DescriptionElement]

    @property
    def text(self) -> str:
        return "".join(str(element) for element in self.elements)

    @classmethod
    def from_runs(cls, description_runs: List[Dict]) -> "Description":
        """parse the description runs into a usable format

        :param description_runs: the original description runs

        :return: List of text (str), timestamp (int) and link values (Link object)
        """
        elements = []
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

        return cls(elements=elements)


def _parse_base_header(header: Dict) -> Dict:
    """parse common left hand side (header) items of an episode or podcast page"""
    strapline = nav(header, ["straplineTextOne"])
    return {
        "author": {
            "name": nav(strapline, [*RUN_TEXT]),
            "id": nav(strapline, ["runs", 0, *NAVIGATION_BROWSE_ID]),
        },
        "title": nav(header, TITLE_TEXT),
    }


def parse_podcast_header(header: Dict) -> Dict:
    metadata = _parse_base_header(header)
    metadata["description"] = nav(header, ["description", *DESCRIPTION_SHELF, *DESCRIPTION], True)
    metadata["saved"] = nav(header, ["buttons", 1, *TOGGLED_BUTTON])

    return metadata


def parse_episode_header(header: Dict) -> Dict:
    metadata = _parse_base_header(header)
    metadata["date"] = nav(header, [*SUBTITLE2])
    metadata["duration"] = nav(header, [*SUBTITLE3], True)
    metadata["saved"] = nav(header, ["buttons", 0, *TOGGLED_BUTTON], True)

    metadata["playlistId"] = None
    menu_buttons = nav(header, ["buttons", -1, "menuRenderer", "items"])
    for button in menu_buttons:
        if nav(button, [MNIR, *ICON_TYPE], True) == "BROADCAST":
            metadata["playlistId"] = nav(button, [MNIR, *NAVIGATION_BROWSE_ID])

    return metadata


def parse_episodes(results) -> List[Dict]:
    episodes = []
    for result in results:
        data = nav(result, ["musicMultiRowListItemRenderer"])
        thumbnails = list(filter(lambda tn: '?' in tn['url'], nav(data, THUMBNAILS)))
        if len(nav(data, SUBTITLE_RUNS)) == 1:
            duration = nav(data, SUBTITLE)
        else:
            date = nav(data, SUBTITLE)
            duration = nav(data, SUBTITLE2, True)
        title = nav(data, TITLE_TEXT)
        description = nav(data, DESCRIPTION, True)
        videoId = nav(data, ["onTap", *WATCH_VIDEO_ID], True)
        browseId = nav(data, [*TITLE, *NAVIGATION_BROWSE_ID], True)
        videoType = nav(data, ["onTap", *NAVIGATION_VIDEO_TYPE], True)
        index = nav(data, ["onTap", "watchEndpoint", "index"])
        episodes.append(
            {
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
        )

    return episodes
