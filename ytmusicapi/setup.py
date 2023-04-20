import argparse
import sys
from pathlib import Path
from typing import Dict

import requests

from ytmusicapi.auth.browser import setup_browser
from ytmusicapi.auth.oauth import YTMusicOAuth


def setup(filepath: str = None, headers_raw: str = None) -> Dict:
    """
    Requests browser headers from the user via command line
    and returns a string that can be passed to YTMusic()

    :param filepath: Optional filepath to store headers to.
    :param headers_raw: Optional request headers copied from browser.
        Otherwise requested from terminal
    :return: configuration headers string
    """
    return setup_browser(filepath, headers_raw)


def setup_oauth(filepath: str = None,
                session: requests.Session = None,
                proxies: dict = None) -> Dict:
    """
    Starts oauth flow from the terminal
    and returns a string that can be passed to YTMusic()

    :param session: Session to use for authentication
    :param proxies: Proxies to use for authentication
    :param filepath: Optional filepath to store headers to.
    :return: configuration headers string
    """
    if not session:
        session = requests.Session()

    return YTMusicOAuth(session, proxies).setup(filepath)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Setup ytmusicapi.')
    parser.add_argument("setup_type",
                        type=str,
                        choices=["oauth", "browser"],
                        help="choose a setup type.")
    parser.add_argument("--file", type=Path, help="optional path to output file.")
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    filename = args.file.as_posix() if args.file else f"{args.setup_type}.json"
    print(f"Creating {filename} with your authentication credentials...")
    func = setup_oauth if args.setup_type == "oauth" else setup
    return func(filename)
