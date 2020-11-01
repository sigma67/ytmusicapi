import pkg_resources
import json
import os
import platform

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

    required_headers = ["Cookie", "X-Goog-AuthUser"]
    required_headers_lower = {v.lower(): v for v in required_headers }
    try:
        headers = {}
        for content in contents:
            header = content.split(': ')
            key = header[0].lower()
            if key in required_headers_lower:
                headers[required_headers_lower[key]] = ': '.join(header[1:])

    except Exception as e:
        raise Exception("Error parsing your input, please try again. Full error: " + str(e))

    if len(headers) != len(required_headers):
        missing = set(required_headers) - set(headers)
        raise Exception(
            "The following entries are missing in your headers: " + ", ".join(missing)
            + ". Please try a different request (such as /browse) and make sure you are logged in."
        )

    with open(pkg_resources.resource_filename('ytmusicapi', 'headers.json')) as json_file:
        default_headers = json.load(json_file)

    default_headers.update(headers)
    if filepath is not None:
        with open(filepath, 'w') as file:
            json.dump(default_headers, file, ensure_ascii=True, indent=4, sort_keys=True)

    return json.dumps(default_headers)
