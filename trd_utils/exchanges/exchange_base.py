import asyncio
import base64
import inspect
import json
import logging
import time
from decimal import Decimal
from typing import Callable

import httpx
from websockets.asyncio.connection import Connection as WSConnection

from trd_utils.exchanges.base_types import (
    UnifiedFuturesMarketInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.http_utils import HttpAsyncClientBase

logger = logging.getLogger(__name__)


class JWTManager:
    _jwt_string: str = None

    def __init__(self, jwt_string: str):
        self._jwt_string = jwt_string
        try:
            payload_b64 = self._jwt_string.split(".")[1]
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
            self.payload = json.loads(payload_bytes)
        except Exception:
            self.payload = {}

    def is_expired(self):
        if "exp" not in self.payload:
            return False

        return time.time() > self.payload["exp"]


class ExchangeBase(HttpAsyncClientBase):
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
    x_router_tag: str = "gray-develop"
    platform_id: str = "10"
    install_channel: str = "officialAPK"
    channel_header: str = "officialAPK"

    # The name of the exchange.
    exchange_name: str = None

    jwt_manager: JWTManager = None

    _fav_letter: str = "^"

    # the lock for internal operations.
    _internal_lock: asyncio.Lock = None

    # extra tasks to be cancelled when the client closes.
    extra_tasks: list[asyncio.Task] = None

    # the price ws connection to be closed when this client is closed.
    price_ws_connection: WSConnection = None
    # endregion
    ###########################################################
    # region constructor method

    def __init__(self):
        self._internal_lock = asyncio.Lock()
        self.extra_tasks = []

    # endregion
    ###########################################################
    # region abstract trading methods

    async def get_unified_trader_positions(
        self,
        uid: int | str,
        min_margin: Decimal = 0,
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

    async def get_unified_futures_market_info(
        self,
        sort_by: str = "percentage_change_24h",
        descending: bool = True,
        allow_delisted: bool = False,
        filter_quote_token: str | None = None,
        raise_on_invalid: bool = False,
        filter_func: Callable | None = None,
    ) -> UnifiedFuturesMarketInfo:
        """
        Returns the unified version of futures market information.
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
    
    def get_platform_name(self) -> str:
        return self.exchange_name

    async def _apply_filter_func(
        self,
        filter_func: Callable,
        func_args: dict,
    ) -> bool:
        if inspect.iscoroutinefunction(filter_func):
            return await filter_func(**func_args)
        elif inspect.isfunction(filter_func) or callable(filter_func):
            result = filter_func(**func_args)
            
            if inspect.iscoroutine(result):
                return await result
            return result
        else:
            raise ValueError("filter_func must be a function or coroutine function.")

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._internal_lock.acquire()
        await self.httpx_client.aclose()

        if self.price_ws_connection:
            try:
                await self.price_ws_connection.close()
            except Exception as ex:
                logger.warning(f"failed to close ws connection: {ex}")

        self._internal_lock.release()

    # endregion
    ###########################################################
    # region data-files related methods

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
