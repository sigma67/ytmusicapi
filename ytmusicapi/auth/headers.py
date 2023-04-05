import json
import os
from typing import Optional, Dict

import requests
from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.oauth import YTMusicOAuth
from ytmusicapi.helpers import initialize_headers


def prepare_headers(session: requests.Session,
                    proxies: Optional[Dict] = None,
                    auth: Optional[str] = None) -> Dict:
    headers = {}
    if auth:
        if os.path.isfile(auth):
            with open(auth) as json_file:
                input_json = json.load(json_file)
        else:
            input_json = json.loads(auth)

        if "oauth.json" in auth:
            oauth = YTMusicOAuth(session, proxies)
            headers = oauth.load_headers(input_json, auth)
        else:
            headers = CaseInsensitiveDict(input_json)

    else:  # no authentication
        headers = initialize_headers()

    return headers
