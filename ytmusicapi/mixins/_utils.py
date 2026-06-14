import json
import re
from datetime import date
from pathlib import Path
from typing import Literal

import requests

from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.type_alias import JsonDict

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


def _resumable_upload(
    file_path: Path,
    upload_endpoint: str,
    headers: JsonDict,
    file_size: int | None = None,
    file_size_limit: int | None = None,
    size_limit_msg: str = "",
    proxies: JsonDict | None = None,
    require_empty_body: bool = False,
) -> JsonDict:
    """Generic resumable file upload using Google's resumable upload protocol.

    Shared between song uploads (uploads.py) and playlist image uploads (playlists.py).

    :param file_path: Path to the file to upload
    :param upload_endpoint: Full URL for the upload endpoint
    :param headers: Headers dict (will be modified in-place for the upload)
    :param file_size: Pre-computed file size in bytes. If None, computed from file_path.
    :param file_size_limit: Maximum allowed file size in bytes (optional)
    :param size_limit_msg: Error message if file exceeds size limit
    :param proxies: Proxies dict for requests
    :param require_empty_body: If True, send empty body on initial POST (for playlist images).
        If False, send filename body (for song uploads).
    :return: Response JSON dict containing encryptedBlobId or upload result
    """
    if not file_path.is_file():
        raise YTMusicUserError("The provided file does not exist.")

    if file_size is None:
        file_size = file_path.stat().st_size

    if file_size_limit is not None and file_size >= file_size_limit:
        raise YTMusicUserError(
            size_limit_msg if size_limit_msg else f"File {file_path} exceeds the size limit of {file_size_limit} bytes"
        )

    headers.pop("content-encoding", None)
    headers["content-type"] = "application/x-www-form-urlencoded;charset=utf-8"
    headers["X-Goog-Upload-Command"] = "start"
    headers["X-Goog-Upload-Header-Content-Length"] = str(file_size)
    headers["X-Goog-Upload-Protocol"] = "resumable"

    body = "" if require_empty_body else ("filename=" + file_path.name).encode("utf-8")

    response = requests.post(
        upload_endpoint,
        data=body,
        headers=headers,
        proxies=proxies,
    )

    upload_url = response.headers["X-Goog-Upload-URL"]
    headers["X-Goog-Upload-Command"] = "upload, finalize"
    headers["X-Goog-Upload-Offset"] = "0"

    with open(file_path, "rb") as file:
        response = requests.post(upload_url, data=file, headers=headers, proxies=proxies)

    if response.status_code != 200:
        raise YTMusicUserError(f"Upload failed with status code {response.status_code}: {response.text}")

    return response.json()
