import argparse
import sys
from pathlib import Path
from typing import Optional

import requests

from ytmusicapi.auth.browser import setup_browser
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken


def setup(filepath: Optional[str] = None, headers_raw: Optional[str] = None) -> str:
    """
    Requests browser headers from the user via command line
    and returns a string that can be passed to YTMusic()

    :param filepath: Optional filepath to store headers to.
    :param headers_raw: Optional request headers copied from browser.
        Otherwise requested from terminal
    :return: configuration headers string
    """
    return setup_browser(filepath, headers_raw)


def setup_oauth(
    filepath: Optional[str] = None,
    session: Optional[requests.Session] = None,
    proxies: Optional[dict] = None,
    open_browser: bool = False,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> RefreshingToken:
    """
    Starts oauth flow from the terminal
    and returns a string that can be passed to YTMusic()

    :param session: Session to use for authentication
    :param proxies: Proxies to use for authentication
    :param filepath: Optional filepath to store headers to.
    :param open_browser: If True, open the default browser with the setup link
    :param client_id: Optional. Used to specify the client_id oauth should use for authentication
        flow. If provided, client_secret MUST also be passed or both will be ignored.
    :param client_secret: Optional. Same as client_id but for the oauth client secret.

    :return: configuration headers string
    """
    if not session:
        session = requests.Session()

    if client_id and client_secret:
        oauth_credentials = OAuthCredentials(client_id, client_secret, session, proxies)

    else:
        oauth_credentials = OAuthCredentials(session=session, proxies=proxies)

    return RefreshingToken.prompt_for_token(oauth_credentials, open_browser, filepath)


def parse_args(args):
    parser = argparse.ArgumentParser(description="Setup ytmusicapi.")
    parser.add_argument("setup_type", type=str, choices=["oauth", "browser"], help="choose a setup type.")
    parser.add_argument("--file", type=Path, help="optional path to output file.")

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    filename = args.file.as_posix() if args.file else f"{args.setup_type}.json"
    print(f"Creating {filename} with your authentication credentials...")
    if args.setup_type == "oauth":
        return setup_oauth(filename, open_browser=True)
    else:
        return setup(filename)
