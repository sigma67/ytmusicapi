import json
import platform

from requests.structures import CaseInsensitiveDict

from ytmusicapi.exceptions import YTMusicError, YTMusicUserError
from ytmusicapi.helpers import *


def is_browser(headers: CaseInsensitiveDict[str]) -> bool:
    browser_structure = {"authorization", "cookie"}
    return all(key in headers for key in browser_structure)


def setup_browser(filepath: str | None = None, headers_raw: str | None = None) -> str:
    contents = []
    if not headers_raw:
        eof = "Ctrl-D" if platform.system() != "Windows" else "'Enter, Ctrl-Z, Enter'"
        print(f"Please paste the request headers from Firefox and press {eof} to continue:")
        while True:
            try:
                line = input()
            except EOFError:
                break
            contents.append(line)
    else:
        contents = headers_raw.split("\n")

    try:
        user_headers = {}
        chrome_remembered_key = ""
        for content in contents:
            header = content.split(": ")
            if header[0].startswith(":"):  # nothing was split or chromium headers
                continue
            if header[0].endswith(":"):  # pragma: no cover
                # weird new chrome "copy-paste in separate lines" format
                chrome_remembered_key = content.replace(":", "")
            if len(header) == 1:
                if chrome_remembered_key:  # pragma: no cover
                    user_headers[chrome_remembered_key] = header[0]
                continue

            user_headers[header[0].lower()] = ": ".join(header[1:])

    except Exception as e:
        raise YTMusicError(f"Error parsing your input, please try again. Full error: {e}") from e

    missing_headers = {"cookie", "x-goog-authuser"} - set(k.lower() for k in user_headers.keys())
    if missing_headers:
        raise YTMusicUserError(
            "The following entries are missing in your headers: "
            + ", ".join(missing_headers)
            + ". Please try a different request (such as /browse) and make sure you are logged in."
        )

    ignore_headers = {"host", "content-length", "accept-encoding"}
    for key in user_headers.copy().keys():
        if key.startswith("sec") or key in ignore_headers:
            user_headers.pop(key, None)

    init_headers = initialize_headers()
    user_headers.update(init_headers)
    headers = user_headers

    if filepath is not None:
        with open(filepath, "w") as file:
            json.dump(headers, file, ensure_ascii=True, indent=4, sort_keys=True)

    return json.dumps(headers)
