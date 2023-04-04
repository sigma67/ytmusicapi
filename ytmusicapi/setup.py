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


if __name__ == "__main__":
    setup_oauth()
