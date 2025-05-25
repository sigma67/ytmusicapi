import json
from pathlib import Path

from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.oauth import OAuthToken
from ytmusicapi.auth.types import AuthType
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.type_alias import JsonDict


def parse_auth_str(auth: str | JsonDict) -> tuple[CaseInsensitiveDict[str], Path | None]:
    """

    :param auth: user-provided auth string or dict
    :return: parsed header dict based on auth, optionally path to file if it auth was a path to a file
    """
    auth_path: Path | None = None
    if isinstance(auth, str):
        auth_str: str = auth
        if auth.startswith("{"):
            input_json = json.loads(auth_str)
        elif (auth_path := Path(auth_str)).is_file():
            with open(auth_path) as json_file:
                input_json = json.load(json_file)
        else:
            raise YTMusicUserError("Invalid auth JSON string or file path provided.")
        return CaseInsensitiveDict(input_json), auth_path

    else:
        return CaseInsensitiveDict(auth), auth_path


def determine_auth_type(auth_headers: CaseInsensitiveDict[str]) -> AuthType:
    """
    Determine the type of auth based on auth headers.

    :param auth_headers: auth headers dict
    :return: AuthType enum
    """
    auth_type = AuthType.OAUTH_CUSTOM_CLIENT
    if OAuthToken.is_oauth(auth_headers):
        auth_type = AuthType.OAUTH_CUSTOM_CLIENT

    if authorization := auth_headers.get("authorization"):
        if "SAPISIDHASH" in authorization:
            auth_type = AuthType.BROWSER
        elif authorization.startswith("Bearer"):
            auth_type = AuthType.OAUTH_CUSTOM_FULL

    return auth_type
