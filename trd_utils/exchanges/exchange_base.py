from decimal import Decimal
from typing import Any
from abc import ABC

import httpx

from trd_utils.exchanges.base_types import UnifiedTraderInfo, UnifiedTraderPositions


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

    # region abstract trading methods

    async def get_unified_trader_positions(
        self,
        uid: int | str,
    ) -> UnifiedTraderPositions:
        """
        Returns the unified version of all currently open positions of the specific
        trader. Note that different exchanges might fill different fields, according to the
        data they provide in their public APIs.
        If you want to fetch past positions history, you have to use another method.
        """
        raise NotImplementedError(
            "This method is not implemented in ExchangeBase class. "
            "Please use a real exchange class inheriting and implementing this method."
        )

    async def get_unified_trader_info(self, uid: int | str) -> UnifiedTraderInfo:
        """
        Returns information about a specific trader.
        Different exchanges might return and fill different information according to the
        data returned from their public APIs.
        """
        raise NotImplementedError(
            "This method is not implemented in ExchangeBase class. "
            "Please use a real exchange class inheriting and implementing this method."
        )

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
