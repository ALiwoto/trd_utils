import asyncio
from decimal import Decimal
import json
import logging
from typing import Type
from abc import ABC

import base64
import time

import httpx
from websockets.asyncio.connection import Connection as WSConnection

from trd_utils.exchanges.base_types import UnifiedTraderInfo, UnifiedTraderPositions
from trd_utils.types_helper.base_model import BaseModel

logger = logging.getLogger(__name__)

class JWTManager():
    _jwt_string: str = None

    def __init__(self, jwt_string: str):
        self._jwt_string = jwt_string
        try:
            payload_b64 = self._jwt_string.split('.')[1]
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + '==')
            self.payload = json.loads(payload_bytes)
        except Exception:
            self.payload = {}

    def is_expired(self):
        if "exp" not in self.payload:
            return False
        
        return time.time() > self.payload["exp"]

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
        headers: dict | None = None,
        params: dict | None = None,
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """
        response = await self.httpx_client.get(
            url=url,
            headers=headers,
            params=params,
        )
        return self._handle_response(
            response=response,
            model_type=model_type,
            parse_float=parse_float,
            raw_data=raw_data,
        )

    async def invoke_post(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        content: dict | str | bytes = "",
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """

        if isinstance(content, dict):
            content = json.dumps(content, separators=(",", ":"), sort_keys=True)

        response = await self.httpx_client.post(
            url=url,
            headers=headers,
            params=params,
            content=content,
        )
        return self._handle_response(
            response=response,
            model_type=model_type,
            parse_float=parse_float,
            raw_data=raw_data,
        )

    def _handle_response(
        self,
        response: httpx.Response,
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        if raw_data:
            return response.content

        j_obj = self._resp_to_json(
            response=response,
            parse_float=parse_float,
        )
        if not model_type:
            return j_obj

        return model_type.deserialize(j_obj)

    def _resp_to_json(
        self,
        response: httpx.Response,
        parse_float=None,
    ):
        try:
            return response.json(parse_float=parse_float)
        except UnicodeDecodeError:
            # try to decompress manually
            import gzip
            import brotli

            content_encoding = response.headers.get("Content-Encoding", "").lower()
            content = response.content

            if "gzip" in content_encoding:
                content = gzip.decompress(content)
            elif "br" in content_encoding:
                content = brotli.decompress(content)
            elif "deflate" in content_encoding:
                import zlib

                content = zlib.decompress(content, -zlib.MAX_WBITS)
            else:
                raise ValueError(
                    f"failed to detect content encoding: {content_encoding}"
                )

            # Now parse the decompressed content
            return json.loads(content.decode("utf-8"), parse_float=parse_float)

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
