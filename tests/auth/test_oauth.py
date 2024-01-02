import json
import time
from pathlib import Path
from typing import Any, Dict
from unittest import mock

import pytest
from requests import Response

from ytmusicapi.auth.types import AuthType
from ytmusicapi.constants import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET
from ytmusicapi.setup import main
from ytmusicapi.ytmusic import OAuthCredentials, YTMusic


@pytest.fixture(name="blank_code")
def fixture_blank_code() -> Dict[str, Any]:
    return {
        "device_code": "",
        "user_code": "",
        "expires_in": 1800,
        "interval": 5,
        "verification_url": "https://www.google.com/device",
    }


@pytest.fixture(name="alt_oauth_credentials")
def fixture_alt_oauth_credentials() -> OAuthCredentials:
    return OAuthCredentials(OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET)


@pytest.fixture(name="yt_alt_oauth")
def fixture_yt_alt_oauth(browser_filepath: str, alt_oauth_credentials: OAuthCredentials) -> YTMusic:
    return YTMusic(browser_filepath, oauth_credentials=alt_oauth_credentials)


class TestOAuth:
    @mock.patch("requests.Response.json")
    @mock.patch("requests.Session.post")
    def test_setup_oauth(self, session_mock, json_mock, oauth_filepath, blank_code, yt_oauth):
        session_mock.return_value = Response()
        fresh_token = yt_oauth._token.as_dict()
        json_mock.side_effect = [blank_code, fresh_token]
        with mock.patch("builtins.input", return_value="y"), mock.patch(
            "sys.argv", ["ytmusicapi", "oauth", "--file", oauth_filepath]
        ):
            main()
            assert Path(oauth_filepath).exists()

        json_mock.side_effect = None
        with open(oauth_filepath, mode="r", encoding="utf8") as oauth_file:
            string_oauth_token = oauth_file.read()

        YTMusic(string_oauth_token)

    def test_oauth_tokens(self, oauth_filepath: str, yt_oauth: YTMusic):
        # ensure instance initialized token
        assert yt_oauth._token is not None

        # set reference file
        with open(oauth_filepath, "r") as f:
            first_json = json.load(f)

        # pull reference values from underlying token
        first_token = yt_oauth._token.access_token
        first_expire = yt_oauth._token.expires_at
        # make token expire
        yt_oauth._token.expires_at = int(time.time())
        # check
        assert yt_oauth._token.is_expiring
        # pull new values, assuming token will be refreshed on access
        second_token = yt_oauth._token.access_token
        second_expire = yt_oauth._token.expires_at
        second_token_inner = yt_oauth._token.access_token
        # check it was refreshed
        assert first_token != second_token
        # check expiration timestamps to confirm
        assert second_expire != first_expire
        assert second_expire > time.time() + 60
        # check token is propagating properly
        assert second_token == second_token_inner

        with open(oauth_filepath, "r") as f2:
            second_json = json.load(f2)

        # ensure token is updating local file
        assert first_json != second_json

    def test_oauth_custom_client(
        self, alt_oauth_credentials: OAuthCredentials, oauth_filepath: str, yt_alt_oauth: YTMusic
    ):
        # ensure client works/ignores alt if browser credentials passed as auth
        assert yt_alt_oauth.auth_type != AuthType.OAUTH_CUSTOM_CLIENT
        with open(oauth_filepath, "r") as f:
            token_dict = json.load(f)
        # oauth token dict entry and alt
        yt_alt_oauth = YTMusic(token_dict, oauth_credentials=alt_oauth_credentials)
        assert yt_alt_oauth.auth_type == AuthType.OAUTH_CUSTOM_CLIENT

    def test_alt_oauth_request(self, yt_alt_oauth: YTMusic, sample_video):
        yt_alt_oauth.get_watch_playlist(sample_video)
