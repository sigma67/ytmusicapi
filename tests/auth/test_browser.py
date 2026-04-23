import json
from pathlib import Path
from unittest import mock

import pytest

import ytmusicapi.setup
from ytmusicapi.setup import main


def _validate_headers(headers_json_as_str):
    """Validate that the headers string is a non-empty json object"""
    try:
        headers_json = json.loads(headers_json_as_str)
    except json.JSONDecodeError:
        pytest.fail("Headers are not a valid JSON string")
    assert isinstance(headers_json, dict), "The headers string did not deserialize to a dictionary"
    assert len(headers_json) > 0, "The resulting headers dict has no keys"


class TestBrowser:
    def test_setup_browser(self, config, tmp_path):
        # Creates a browser.json that gets used for subsequent tests
        headers_raw = config["auth"]["headers_raw"]
        tmp_file = str(tmp_path / "browser.json")
        headers = ytmusicapi.setup(tmp_file, headers_raw)
        assert len(headers) >= 2
        headers_raw_lines = headers_raw.split("\n")
        with (
            mock.patch("sys.argv", ["ytmusicapi", "browser", "--file", tmp_file]),
            mock.patch("builtins.input", side_effect=([*headers_raw_lines, EOFError()])),
        ):
            headers = main()
            assert len(headers) >= 2

    @pytest.mark.parametrize(
        "raw_headers_path",
        ["raw_chrome_headers.txt", "raw_firefox_headers.txt"],
    )
    def test_setup_browser_multiple_formats(self, tmp_path, raw_headers_path):
        # Temp browser.json -- does not collide with browser.json from prev test
        browser_filepath = str(tmp_path / "browser.json")

        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / raw_headers_path, encoding="utf8") as f:
            raw_headers = f.read()

        # Verify by calling setup() directly
        headers_json_as_str: str = ytmusicapi.setup(browser_filepath, raw_headers)
        _validate_headers(headers_json_as_str)

        # Verify through CLI
        raw_headers = raw_headers.split("\n")
        with (
            mock.patch("sys.argv", ["ytmusicapi", "browser", "--file", browser_filepath]),
            mock.patch("builtins.input", side_effect=([*raw_headers, EOFError()])),
        ):
            headers_json_as_str: str = main()
            _validate_headers(headers_json_as_str)
