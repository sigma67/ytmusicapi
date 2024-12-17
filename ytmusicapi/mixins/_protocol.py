"""protocol that defines the functions available to mixins"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional, Protocol

from requests import Response
from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.types import AuthType
from ytmusicapi.parsers.i18n import Parser


class MixinProtocol(Protocol):
    """protocol that defines the functions available to mixins"""

    auth_type: AuthType

    parser: Parser

    proxies: Optional[dict[str, str]]

    def _check_auth(self) -> None:
        """checks if self has authentication"""

    def _send_request(self, endpoint: str, body: dict, additionalParams: str = "") -> dict:
        """for sending post requests to YouTube Music"""

    def _send_get_request(self, url: str, params: Optional[dict] = None) -> Response:
        """for sending get requests to YouTube Music"""

    @contextmanager
    def as_mobile(self) -> Iterator[None]:
        """context-manager, that allows requests as the YouTube Music Mobile-App"""

    @property
    def headers(self) -> CaseInsensitiveDict[str]:
        """property for getting request headers"""
