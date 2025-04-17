import argparse
import importlib.metadata
import sys
from pathlib import Path

import requests

from ytmusicapi.auth.browser import setup_browser
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken


def setup(filepath: str | None = None, headers_raw: str | None = None) -> str:
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
    client_id: str,
    client_secret: str,
    filepath: str | None = None,
    session: requests.Session | None = None,
    proxies: dict[str, str] | None = None,
    open_browser: bool = False,
) -> RefreshingToken:
    """
    Starts oauth flow from the terminal
    and returns a string that can be passed to YTMusic()

    :param client_id: Optional. Used to specify the client_id oauth should use for authentication
        flow. If provided, client_secret MUST also be passed or both will be ignored.
    :param client_secret: Optional. Same as client_id but for the oauth client secret.
    :param session: Session to use for authentication
    :param proxies: Proxies to use for authentication
    :param filepath: Optional filepath to store headers to.
    :param open_browser: If True, open the default browser with the setup link

    :return: configuration headers string
    """
    if not session:
        session = requests.Session()

    oauth_credentials = OAuthCredentials(client_id, client_secret, session, proxies)

    return RefreshingToken.prompt_for_token(oauth_credentials, open_browser, filepath)


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Setup ytmusicapi.")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"ytmusicapi {importlib.metadata.version('ytmusicapi')}",
        help="Installed version of ytmusicapi",
    )
    # parser.add_argument("setup_type", type=str, choices=["oauth", "browser"], help="choose a setup type.")
    subparsers = parser.add_subparsers(help="choose a setup type.", dest="setup_type", required=True)
    oauth_parser = subparsers.add_parser(
        "oauth",
        help="create an oauth token using your Google Youtube API credentials; type 'ytmusicapi oauth -h' for details.",
    )
    oauth_parser.add_argument("--file", type=Path, help="optional path to output file")
    oauth_parser.add_argument("--client-id", type=str, help="use your Google Youtube API client ID.")
    oauth_parser.add_argument("--client-secret", type=str, help="use your Google Youtube API client secret.")
    browser_parser = subparsers.add_parser(
        "browser",
        help="use cookies from request headers (deprecated); type 'ytmusicapi browser -h' for details.",
    )
    browser_parser.add_argument("--file", type=Path, help="optional path to output file.")

    return parser.parse_args(args)


def main() -> RefreshingToken | str:
    args = parse_args(sys.argv[1:])
    filename = args.file.as_posix() if args.file else f"{args.setup_type}.json"
    print(f"Creating {Path(filename).resolve().as_uri()} with your authentication credentials...")
    if args.setup_type == "oauth":
        if args.client_id is None:
            args.client_id = input("Enter your Google Youtube Data API client ID: ")
        if args.client_secret is None:
            args.client_secret = input("Enter your Google Youtube Data API client secret: ")
        return setup_oauth(
            client_id=args.client_id, client_secret=args.client_secret, filepath=filename, open_browser=True
        )
    else:
        return setup(filename)
