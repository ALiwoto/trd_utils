
from decimal import Decimal
from typing import Any
from abc import ABC

import httpx


class ExchangeBase(ABC):
    ###########################################################
    # region client parameters
    user_agent: str = "okhttp/4.12.0"
    x_requested_with: str = None
    httpx_client: httpx.AsyncClient = None
    account_name: str = "default"
    sessions_dir: str = "sessions"

    authorization_token: str = None
    device_id: str = None
    trace_id: str = None
    app_version: str = "4.28.3"
    platform_id: str = "10"
    install_channel: str = "officialAPK"
    channel_header: str = "officialAPK"

    _fav_letter: str = "^"
    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(self, payload=None, needs_auth: bool = False) -> dict:
        pass

    async def invoke_get(
        self,
        url: str,
        headers: dict | None,
        params: dict | None,
        model: Any,
        parse_float=Decimal,
    ) -> Any:
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """
        pass

    async def invoke_post(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        content: str | bytes = "",
        model: None = None,
        parse_float=Decimal,
    ):
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """
        pass

    async def aclose(self) -> None:
        pass

    def read_from_session_file(self, file_path: str) -> None:
        """
        Reads from session file; if it doesn't exist, creates it.
        """
        pass

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """
        pass

    # endregion
    ###########################################################
