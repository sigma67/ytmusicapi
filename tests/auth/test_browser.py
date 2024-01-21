from unittest import mock

import ytmusicapi.setup
from ytmusicapi.setup import main


class TestBrowser:
    def test_setup_browser(self, config, browser_filepath: str):
        headers = ytmusicapi.setup(browser_filepath, config["auth"]["headers_raw"])
        assert len(headers) >= 2
        headers_raw = config["auth"]["headers_raw"].split("\n")
        with (
            mock.patch("sys.argv", ["ytmusicapi", "browser", "--file", browser_filepath]),
            mock.patch("builtins.input", side_effect=([*headers_raw, EOFError()])),
        ):
            headers = main()
            assert len(headers) >= 2
