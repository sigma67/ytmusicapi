import os
import platform
from ytmusicapi.helpers import *

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


def setup(filepath=None, headers_raw=None):
    contents = []
    if not headers_raw:
        eof = "Ctrl-D" if platform.system() != "Windows" else "'Enter, Ctrl-Z, Enter'"
        print("Please paste the request headers from Firefox and press " + eof + " to continue:")
        while True:
            try:
                line = input()
            except EOFError:
                break
            contents.append(line)
    else:
        contents = headers_raw.split('\n')

    try:
        user_headers = {}
        for content in contents:
            header = content.split(': ')
            if len(header) == 1 or header[0].startswith(
                    ":"):  # nothing was split or chromium headers
                continue
            user_headers[header[0].lower()] = ': '.join(header[1:])

    except Exception as e:
        raise Exception("Error parsing your input, please try again. Full error: " + str(e))

    missing_headers = {"cookie", "x-goog-authuser"} - set(k.lower() for k in user_headers.keys())
    if missing_headers:
        raise Exception(
            "The following entries are missing in your headers: " + ", ".join(missing_headers)
            + ". Please try a different request (such as /browse) and make sure you are logged in."
        )

    ignore_headers = {"host", "content-length", "accept-encoding"}
    for i in ignore_headers:
        user_headers.pop(i, None)

    init_headers = initialize_headers()
    user_headers.update(init_headers)
    headers = user_headers

    if filepath is not None:
        with open(filepath, 'w') as file:
            json.dump(headers, file, ensure_ascii=True, indent=4, sort_keys=True)

    return json.dumps(headers)
