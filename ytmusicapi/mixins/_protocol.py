"""protocol that defines the functions available to mixins"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Protocol

from requests import Response
from requests.structures import CaseInsensitiveDict

from ytmusicapi.auth.types import AuthType
from ytmusicapi.parsers.i18n import Parser
from ytmusicapi.type_alias import JsonDict


class MixinProtocol(Protocol):
    """protocol that defines the functions available to mixins"""

    auth_type: AuthType

    parser: Parser

    proxies: dict[str, str] | None

    @property
    def uses_tv_client(self) -> bool:
        """whether requests are sent as YouTube's TV client (OAuth authentication)"""

    def _send_data_api_request(
        self, method: str, resource: str, params: JsonDict | None = None, body: JsonDict | None = None
    ) -> JsonDict:
        """for sending requests to the YouTube Data API v3 (OAuth authentication only)"""

    def _check_auth(self) -> None:
        """checks if self has authentication"""

    def _send_request(self, endpoint: str, body: JsonDict, additionalParams: str = "") -> JsonDict:
        """for sending post requests to YouTube Music"""

    def _send_get_request(self, url: str, params: JsonDict | None = None) -> Response:
        """for sending get requests to YouTube Music"""

    @contextmanager
    def as_mobile(self) -> Iterator[None]:
        """context-manager, that allows requests as the YouTube Music Mobile-App"""

    @property
    def headers(self) -> CaseInsensitiveDict[str]:
        """property for getting request headers"""
