from unittest import mock

import ytmusicapi.setup
from ytmusicapi.setup import main


class TestBrowser:
    def test_setup_browser(self, config, tmp_path):
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
