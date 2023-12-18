import json
import os
from typing import Dict, Optional

import requests
from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.browser import is_browser
from ytmusicapi.auth.oauth import OAuthCredentials, YTMusicOAuth, is_oauth, is_custom_oauth
from ytmusicapi.helpers import initialize_headers


def load_headers_file(auth: str) -> Dict:
    if os.path.isfile(auth):
        with open(auth) as json_file:
            input_json = json.load(json_file)
        input_json['filepath'] = auth
    else:
        input_json = json.loads(auth)

    return input_json


def prepare_headers(session: requests.Session,
                    proxies: Optional[Dict] = None,
                    input_dict: Optional[CaseInsensitiveDict] = None,
                    oauth_credentials: Optional[OAuthCredentials] = None
                    ) -> Dict:
    """

    :param session: Either the session to be used when creating a YTMusicOAuth
        instance or the YTMusicOAuth instance itself.
    :param proxies: Optional. Proxy configuration parameters passed to session.
        Ignored if YTMusicOAuth instance passed to function.
    :param input_dict: Optional. Either completed browser auth headers or oauth token.
    :param oauth_credentials: Optional. An instance of OAuthCredentials to use for authentication flow.
        (Default = None)
    """

    if input_dict:
        if is_oauth(input_dict):
            oauth = YTMusicOAuth(session, proxies, oauth_credentials=oauth_credentials)
            headers = oauth.load_headers(dict(input_dict), input_dict.get('filepath'))

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
