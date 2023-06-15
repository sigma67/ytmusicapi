import json
import os
from typing import Dict, Optional

import requests
from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.browser import is_browser
from ytmusicapi.auth.oauth import YTMusicOAuth, is_oauth, is_custom_oauth
from ytmusicapi.helpers import initialize_headers


def load_headers_file(auth: str) -> Dict:
    if os.path.isfile(auth):
        with open(auth) as json_file:
            input_json = json.load(json_file)
    else:
        input_json = json.loads(auth)

    return input_json


def prepare_headers(
    session: requests.Session,
    proxies: Optional[Dict] = None,
    auth: Optional[str] = None,
) -> Dict:
    if auth:
        input_json = load_headers_file(auth)
        input_dict = CaseInsensitiveDict(input_json)

        if is_oauth(input_dict):
            oauth = YTMusicOAuth(session, proxies)
            headers = oauth.load_headers(dict(input_dict), auth)

        elif is_browser(input_dict):
            headers = input_dict

        elif is_custom_oauth(input_dict):
            headers = input_dict

        else:
            raise Exception(
                "Could not detect credential type. "
                "Please ensure your oauth or browser credentials are set up correctly.")

    else:  # no authentication
        headers = initialize_headers()

    return headers
