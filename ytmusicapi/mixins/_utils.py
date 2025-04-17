import re
from datetime import date
from typing import Literal

from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.models.content.enums import LikeStatus

LibraryOrderType = Literal["a_to_z", "z_to_a", "recently_added"]


def prepare_like_endpoint(rating: str | LikeStatus) -> str:
    match rating:
        case LikeStatus.LIKE:
            return "like/like"
        case LikeStatus.DISLIKE:
            return "like/dislike"
        case LikeStatus.INDIFFERENT:
            return "like/removelike"
        case _:
            raise YTMusicUserError(
                f"Invalid rating provided. Use one of {[e.value for e in LikeStatus.__members__.values()]}."
            )


def validate_order_parameter(order: LibraryOrderType | None) -> None:
    """Validate the provided order, if any

    :raises YTMusicUserError: if the provided order is invalid
    """
    orders = ["a_to_z", "z_to_a", "recently_added"]
    if order and order not in orders:
        raise YTMusicUserError(
            "Invalid order provided. Please use one of the following orders or leave out the parameter: "
            + ", ".join(orders)
        )


def prepare_order_params(order: LibraryOrderType) -> str:
    """Returns request params belonging to a specific sorting order."""
    orders = ["a_to_z", "z_to_a", "recently_added"]
    # determine order_params via `.contents.singleColumnBrowseResultsRenderer.tabs[0].tabRenderer.content.sectionListRenderer.contents[1].itemSectionRenderer.header.itemSectionTabbedHeaderRenderer.endItems[1].dropdownRenderer.entries[].dropdownItemRenderer.onSelectCommand.browseEndpoint.params` of `/youtubei/v1/browse` response
    order_params = ["ggMGKgQIARAA", "ggMGKgQIARAB", "ggMGKgQIABAB"]
    return order_params[orders.index(order)]


def html_to_txt(html_text: str) -> str:
    """
    Sanitize tags from html

    :param html_text: String containing html tags.
    :return: String without < > characters
    """
    tags = re.findall("<[^>]+>", html_text)
    for tag in tags:
        html_text = html_text.replace(tag, "")
    return html_text


def get_datestamp() -> int:
    """Returns the number of days since January 1, 1970.
    Currently only used for the signature timestamp in :py:func:`get_song`."""
    return (date.today() - date.fromtimestamp(0)).days
