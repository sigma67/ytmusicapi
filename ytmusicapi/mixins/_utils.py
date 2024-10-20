import re
from datetime import date
from typing import Literal

from ytmusicapi.exceptions import YTMusicUserError

LibraryOrderType = Literal["a_to_z", "z_to_a", "recently_added"]


def prepare_like_endpoint(rating):
    if rating == "LIKE":
        return "like/like"
    elif rating == "DISLIKE":
        return "like/dislike"
    elif rating == "INDIFFERENT":
        return "like/removelike"
    else:
        return None


def validate_order_parameter(order):
    orders = ["a_to_z", "z_to_a", "recently_added"]
    if order and order not in orders:
        raise YTMusicUserError(
            "Invalid order provided. Please use one of the following orders or leave out the parameter: "
            + ", ".join(orders)
        )


def prepare_order_params(order: LibraryOrderType):
    orders = ["a_to_z", "z_to_a", "recently_added"]
    if order is not None:
        # determine order_params via `.contents.singleColumnBrowseResultsRenderer.tabs[0].tabRenderer.content.sectionListRenderer.contents[1].itemSectionRenderer.header.itemSectionTabbedHeaderRenderer.endItems[1].dropdownRenderer.entries[].dropdownItemRenderer.onSelectCommand.browseEndpoint.params` of `/youtubei/v1/browse` response
        order_params = ["ggMGKgQIARAA", "ggMGKgQIARAB", "ggMGKgQIABAB"]
        return order_params[orders.index(order)]


def html_to_txt(html_text):
    tags = re.findall("<[^>]+>", html_text)
    for tag in tags:
        html_text = html_text.replace(tag, "")
    return html_text


def get_datestamp():
    return (date.today() - date.fromtimestamp(0)).days
