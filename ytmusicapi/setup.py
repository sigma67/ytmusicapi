import pkg_resources
import json
import os
import platform

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


def setup(filepath=None):
    eof = "Ctrl-D" if platform.system() != "Windows" else "'Enter, Ctrl-Z, Enter'"
    print("Please paste the request headers from Firefox and press " + eof + " to continue:")

    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    required_headers = ["Cookie"]
    try:
        headers = {}
        for content in contents:
            header = content.split(': ')
            key = header[0]
            if key in required_headers:
                headers[key] = ': '.join(header[1:])

    except Exception as e:
        raise Exception("Error parsing your input, please try again. Full error: " + str(e))

    if len(headers) != len(required_headers):
        missing = set(required_headers) - set(headers)
        raise Exception("The following entries are missing in your headers: " + ", ".join(missing) +
                        ". Please try a different request (such as /browse) and make sure you are logged in.")

    with open(pkg_resources.resource_filename('ytmusicapi', 'headers.json')) as json_file:
        default_headers = json.load(json_file)

    headers.update(default_headers)
    if filepath is not None:
        with open(filepath, 'w') as file:
            json.dump(headers, file, ensure_ascii=True, indent=4, sort_keys=True)

    return json.dumps(headers)
