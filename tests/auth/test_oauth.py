import json
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest
from requests import Response

from ytmusicapi.auth.oauth import OAuthToken, RefreshingToken
from ytmusicapi.auth.types import AuthType
from ytmusicapi.exceptions import YTMusicServerError, YTMusicUserError
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
        with tempfile.NamedTemporaryFile(delete=False) as f:
            oauth_filepath = f.name
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

    def test_setup_oauth_uses_refresh_token_expiration(self, blank_code):
        credentials = mock.Mock()
        credentials.get_code.return_value = blank_code
        credentials.token_from_code.return_value = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
            "scope": "https://www.googleapis.com/auth/youtube",
            "token_type": "Bearer",
            "refresh_token_expires_in": 604799,
        }

        with (
            mock.patch("builtins.input", return_value=""),
            mock.patch("ytmusicapi.auth.oauth.token.time.time", return_value=1000),
        ):
            token = RefreshingToken.prompt_for_token(credentials)
            assert token.access_token == "test_access_token"
            assert token.refresh_token == "test_refresh_token"
            assert token.expires_at == 4600
            assert token.expires_in == 604799
            assert not hasattr(token, "refresh_token_expires_in")

    @pytest.fixture(name="token_response")
    def fixture_token_response(self) -> JsonDict:
        return {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
            "scope": "https://www.googleapis.com/auth/youtube",
            "token_type": "Bearer",
        }

    def test_setup_oauth_non_interactive_polls_until_authorized(self, blank_code, token_response):
        """Regression for #777: without a TTY there is no one to press Enter, so the
        flow must poll the token endpoint instead of calling ``input()``."""
        credentials = mock.Mock()
        credentials.get_code.return_value = blank_code
        credentials.token_from_code.side_effect = [
            {"error": "authorization_pending"},
            {"error": "slow_down"},
            token_response,
        ]

        with (
            mock.patch("builtins.input", side_effect=EOFError) as input_mock,
            mock.patch("ytmusicapi.auth.oauth.token.time.sleep") as sleep_mock,
        ):
            token = RefreshingToken.prompt_for_token(credentials, interactive=False)

        input_mock.assert_not_called()
        assert token.access_token == "test_access_token"
        assert token.refresh_token == "test_refresh_token"
        assert credentials.token_from_code.call_count == 3
        # slow_down adds 5 seconds to the polling interval, as per the device flow spec
        assert [call.args[0] for call in sleep_mock.call_args_list] == [5, 10]

    @pytest.mark.parametrize("error", ["access_denied", "expired_token"])
    def test_setup_oauth_non_interactive_stops_on_error(self, blank_code, error):
        credentials = mock.Mock()
        credentials.get_code.return_value = blank_code
        credentials.token_from_code.return_value = {"error": error}

        with (
            mock.patch("ytmusicapi.auth.oauth.token.time.sleep") as sleep_mock,
            pytest.raises(YTMusicServerError, match=error),
        ):
            RefreshingToken.prompt_for_token(credentials, interactive=False)

        sleep_mock.assert_not_called()

    def test_setup_oauth_non_interactive_times_out(self, blank_code):
        credentials = mock.Mock()
        credentials.get_code.return_value = {**blank_code, "expires_in": 10, "interval": 5}
        credentials.token_from_code.return_value = {"error": "authorization_pending"}

        with (
            mock.patch("ytmusicapi.auth.oauth.token.time.monotonic", side_effect=[0, 4, 8, 12]),
            mock.patch("ytmusicapi.auth.oauth.token.time.sleep"),
            pytest.raises(YTMusicServerError, match="expired"),
        ):
            RefreshingToken.prompt_for_token(credentials, interactive=False)

    def test_setup_oauth_cli_non_interactive_flag(self, blank_code, token_response, tmp_path):
        credentials = mock.Mock()
        credentials.get_code.return_value = blank_code
        credentials.token_from_code.return_value = token_response
        oauth_filepath = tmp_path / "oauth.json"

        with (
            mock.patch("ytmusicapi.setup.OAuthCredentials", return_value=credentials),
            mock.patch("builtins.input", side_effect=EOFError) as input_mock,
            mock.patch("webbrowser.open"),
            mock.patch(
                "sys.argv",
                [
                    "ytmusicapi",
                    "oauth",
                    "--file",
                    str(oauth_filepath),
                    "--client-id",
                    "test_id",
                    "--client-secret",
                    "test_secret",
                    "--non-interactive",
                ],
            ),
        ):
            main()

        input_mock.assert_not_called()
        assert OAuthToken.is_oauth(json.loads(oauth_filepath.read_text(encoding="utf8")))

    def test_setup_oauth_cli_non_interactive_requires_client_credentials(self, capsys):
        with (
            mock.patch("sys.argv", ["ytmusicapi", "oauth", "--non-interactive"]),
            pytest.raises(SystemExit),
        ):
            main()

        assert "--client-id" in capsys.readouterr().err

    def test_oauth_token_dict_ignores_unexpected_fields(self):
        """Regression for #887 / #921: a saved oauth.json may contain extra
        fields like ``refresh_token_expires_in`` (added to Google's device-flow
        response). Loading such a token via ``YTMusic`` must not crash on the
        strict Token dataclass.
        """
        credentials = mock.Mock(spec=OAuthCredentials)
        token_dict = {
            "scope": "https://www.googleapis.com/auth/youtube",
            "token_type": "Bearer",
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": int(time.time()) + 3600,
            "expires_in": 3600,
            "refresh_token_expires_in": 604799,
        }

        yt = YTMusic(token_dict, oauth_credentials=credentials)

        assert yt.auth_type == AuthType.OAUTH_CUSTOM_CLIENT
        assert yt._token is not None
        assert yt._token.refresh_token == "test_refresh_token"
        assert not hasattr(yt._token, "refresh_token_expires_in")

    def test_from_json_missing_file_raises_filenotfound(self, tmp_path):
        """Regression for #954: loading a non-existent path should raise
        FileNotFoundError naming the path, not UnboundLocalError.
        """
        missing = tmp_path / "does-not-exist.json"
        with pytest.raises(FileNotFoundError):
            OAuthToken.from_json(missing)

    @pytest.mark.skip(reason="oauth is currently not working, see #813")
    def test_oauth_tokens(self, oauth_filepath: str, yt_oauth: YTMusic):
        # ensure instance initialized token
        assert yt_oauth._token is not None

        # set reference file
        with open(oauth_filepath, encoding="utf-8") as f:
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

        with open(oauth_filepath, encoding="utf-8") as f2:
            second_json = json.load(f2)

        # ensure token is updating local file
        assert first_json != second_json

    def test_oauth_custom_client(
        self, alt_oauth_credentials: OAuthCredentials, oauth_filepath: str, yt_alt_oauth: YTMusic
    ):
        # ensure client works/ignores alt if browser credentials passed as auth
        assert yt_alt_oauth.auth_type != AuthType.OAUTH_CUSTOM_CLIENT
        with open(oauth_filepath, encoding="utf-8") as f:
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
