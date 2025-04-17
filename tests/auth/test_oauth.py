import json
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest
from requests import Response

from ytmusicapi.auth.oauth import OAuthToken
from ytmusicapi.auth.types import AuthType
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.setup import main
from ytmusicapi.type_alias import JsonDict
from ytmusicapi.ytmusic import OAuthCredentials, YTMusic


@pytest.fixture(name="blank_code")
def fixture_blank_code() -> JsonDict:
    return {
        "device_code": "",
        "user_code": "",
        "expires_in": 1800,
        "interval": 5,
        "verification_url": "https://www.google.com/device",
    }


@pytest.fixture(name="alt_oauth_credentials")
def fixture_alt_oauth_credentials(config) -> OAuthCredentials:
    return OAuthCredentials(config["auth"]["client_id"], config["auth"]["client_secret"])


@pytest.fixture(name="yt_alt_oauth")
def fixture_yt_alt_oauth(browser_filepath: str, alt_oauth_credentials: OAuthCredentials) -> YTMusic:
    return YTMusic(browser_filepath, oauth_credentials=alt_oauth_credentials)


class TestOAuth:
    @mock.patch("requests.Response.json")
    @mock.patch("requests.Session.post")
    def test_setup_oauth(self, session_mock, json_mock, blank_code, config):
        session_mock.return_value = Response()
        token_code = json.loads(config["auth"]["oauth_token"])
        json_mock.side_effect = [blank_code, token_code]
        oauth_file = tempfile.NamedTemporaryFile(delete=False)
        oauth_filepath = oauth_file.name
        with (
            mock.patch("builtins.input", return_value="y"),
            mock.patch(
                "sys.argv",
                [
                    "ytmusicapi",
                    "oauth",
                    "--file",
                    oauth_filepath,
                    "--client-id",
                    "test_id",
                    "--client-secret",
                    "test_secret",
                ],
            ),
            mock.patch("webbrowser.open"),
        ):
            main()
            assert Path(oauth_filepath).exists()

        json_mock.side_effect = None
        with open(oauth_filepath, encoding="utf8") as oauth_file:
            oauth_token = json.loads(oauth_file.read())

        assert oauth_token["expires_at"] != 0
        assert OAuthToken.is_oauth(oauth_token)

        oauth_file.close()
        Path(oauth_file.name).unlink()

    def test_oauth_tokens(self, oauth_filepath: str, yt_oauth: YTMusic):
        # ensure instance initialized token
        assert yt_oauth._token is not None

        # set reference file
        with open(oauth_filepath) as f:
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

        with open(oauth_filepath) as f2:
            second_json = json.load(f2)

        # ensure token is updating local file
        assert first_json != second_json

    def test_oauth_custom_client(
        self, alt_oauth_credentials: OAuthCredentials, oauth_filepath: str, yt_alt_oauth: YTMusic
    ):
        # ensure client works/ignores alt if browser credentials passed as auth
        assert yt_alt_oauth.auth_type != AuthType.OAUTH_CUSTOM_CLIENT
        with open(oauth_filepath) as f:
            token_dict = json.load(f)

        # oauth token dict entry and alt
        yt_alt_oauth = YTMusic(token_dict, oauth_credentials=alt_oauth_credentials)
        assert yt_alt_oauth.auth_type == AuthType.OAUTH_CUSTOM_CLIENT

        # forgot to pass OAuth credentials - should raise
        with pytest.raises(YTMusicUserError):
            YTMusic(token_dict)

        # oauth custom full
        token_dict["authorization"] = "Bearer DKLEK23"
        yt_alt_oauth = YTMusic(token_dict, oauth_credentials=alt_oauth_credentials)
        assert yt_alt_oauth.auth_type == AuthType.OAUTH_CUSTOM_FULL

    def test_alt_oauth_request(self, yt_alt_oauth: YTMusic, sample_video):
        yt_alt_oauth.get_watch_playlist(sample_video)
