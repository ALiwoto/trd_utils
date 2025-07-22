import asyncio
from decimal import Decimal
import json
import logging
import httpx

import time
from pathlib import Path

from trd_utils.date_utils.datetime_helpers import dt_from_ts
from trd_utils.exchanges.base_types import (
    UnifiedPositionInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.exchanges.blofin.blofin_types import (
    CmsColorResponse,
    CopyTraderAllOrderHistory,
    CopyTraderAllOrderList,
    CopyTraderInfoResponse,
    CopyTraderOrderHistoryResponse,
    CopyTraderOrderListResponse,
    ShareConfigResponse,
)
from trd_utils.cipher import AESCipher
from trd_utils.exchanges.errors import ExchangeError
from trd_utils.exchanges.exchange_base import ExchangeBase


BASE_PROFILE_URL = "https://blofin.com/copy-trade/details/"

logger = logging.getLogger(__name__)


class BlofinClient(ExchangeBase):
    ###########################################################
    # region client parameters
    blofin_api_base_host: str = "https://\u0062lofin.co\u006d"
    blofin_api_base_url: str = "https://\u0062lofin.co\u006d/uapi/v1"
    origin_header: str = "https://\u0062lofin.co\u006d"

    timezone: str = "Etc/UTC"

    # endregion
    ###########################################################
    # region client constructor
    def __init__(
        self,
        account_name: str = "default",
        http_verify: bool = True,
        fav_letter: str = "^",
        read_session_file: bool = True,
        sessions_dir: str = "sessions",
        use_http1: bool = False,
        use_http2: bool = True,
    ):
        self.httpx_client = httpx.AsyncClient(
            verify=http_verify,
            http1=use_http1,
            http2=use_http2,
        )
        self.account_name = account_name
        self._fav_letter = fav_letter
        self.sessions_dir = sessions_dir
        self.exchange_name = "blofin"

        super().__init__()

        if read_session_file:
            self.read_from_session_file(f"{sessions_dir}/{self.account_name}.bf")

    # endregion
    ###########################################################
    # region v1/cms/
    async def get_share_config(self) -> ShareConfigResponse:
        headers = self.get_headers()
        return await self.invoke_get(
            f"{self.blofin_api_base_url}/cms/share_config",
            headers=headers,
            model_type=ShareConfigResponse,
        )

    async def get_cms_color(self) -> CmsColorResponse:
        headers = self.get_headers()
        return await self.invoke_get(
            f"{self.blofin_api_base_url}/cms/color",
            headers=headers,
            model_type=CmsColorResponse,
        )

    # endregion
    ###########################################################
    # region copy/trader
    async def get_copy_trader_info(self, uid: int) -> CopyTraderInfoResponse:
        payload = {
            "uid": uid,
        }
        headers = self.get_headers()
        return await self.invoke_post(
            f"{self.blofin_api_base_url}/copy/trader/info",
            headers=headers,
            content=payload,
            model_type=CopyTraderInfoResponse,
        )

    async def get_copy_trader_order_list(
        self,
        uid: int | str,
        from_param: int = 0,
        limit_param: int = 20,
    ) -> CopyTraderOrderListResponse:
        payload = {
            "from": from_param,
            "limit": limit_param,
            "uid": int(uid),
        }
        headers = self.get_headers()
        return await self.invoke_post(
            f"{self.blofin_api_base_url}/copy/trader/order/list",
            headers=headers,
            content=payload,
            model_type=CopyTraderOrderListResponse,
        )

    async def get_copy_trader_all_order_list(
        self,
        uid: int,
        from_param: int = 0,
        chunk_limit: int = 20,
        sleep_delay: int = 0.5,
    ) -> CopyTraderAllOrderList:
        if chunk_limit < 1:
            raise ValueError("chunk_limit parameter has to be more than 1")

        result = CopyTraderAllOrderList(
            code=200,
            data=[],
            total_count=0,
        )
        current_id_from = from_param
        while True:
            total_ignored = 0
            current_result = await self.get_copy_trader_order_list(
                uid=uid,
                from_param=current_id_from,
                limit_param=chunk_limit,
            )
            if current_result.code != 200:
                if current_result.msg:
                    raise ExchangeError(
                        f"blofin get_copy_trader_all_order_list: {current_result.msg}; "
                        f"code: {current_result.code}"
                    )
                raise ExchangeError(
                    "blofin get_copy_trader_all_order_list: unknown error; "
                    f"code: {current_result.code}"
                )

            if not isinstance(current_result, CopyTraderOrderListResponse):
                raise ValueError(
                    "get_copy_trader_order_list returned invalid value of "
                    f"{type(current_result)}",
                )
            if not current_result.data:
                # we no longer have anything else here
                return result

            if current_result.data[0].id == current_id_from:
                if len(current_result.data) < 2:
                    return result
                current_result.data = current_result.data[1:]
                total_ignored += 1
            elif current_id_from:
                raise ValueError(
                    "Expected first array to have the same value as from_param: "
                    f"current_id_from: {current_id_from}; but was: {current_result.data[0].id}"
                )

            current_id_from = current_result.data[-1].id
            result.data.extend(current_result.data)
            result.total_count += len(current_result.data)
            if len(current_result.data) < chunk_limit - total_ignored:
                # the trader doesn't have any more open orders
                return result
            if result.total_count > len(current_result.data) and sleep_delay:
                # we don't want to sleep after 1 request only
                await asyncio.sleep(sleep_delay)

    async def get_copy_trader_order_history(
        self,
        uid: int,
        from_param: int = 0,
        limit_param: int = 20,
    ) -> CopyTraderOrderHistoryResponse:
        payload = {
            "from": from_param,
            "limit": limit_param,
            "uid": uid,
        }
        headers = self.get_headers()
        return await self.invoke_post(
            f"{self.blofin_api_base_url}/copy/trader/order/history",
            headers=headers,
            content=payload,
            model_type=CopyTraderOrderHistoryResponse,
        )

    async def get_copy_trader_all_order_history(
        self,
        uid: int,
        from_param: int = 0,
        chunk_limit: int = 20,
        sleep_delay: int = 0.5,
    ) -> CopyTraderAllOrderHistory:
        if chunk_limit < 1:
            raise ValueError("chunk_limit parameter has to be more than 1")

        result = CopyTraderAllOrderHistory(
            code=200,
            data=[],
            total_count=0,
        )
        current_id_from = from_param
        while True:
            total_ignored = 0
            current_result = await self.get_copy_trader_order_history(
                uid=uid,
                from_param=current_id_from,
                limit_param=chunk_limit,
            )
            if (
                not current_result
                or not isinstance(current_result, CopyTraderOrderHistoryResponse)
                or not current_result.data
            ):
                return result

            if current_result.data[0].id == current_id_from:
                if len(current_result.data) < 2:
                    return result
                current_result.data = current_result.data[1:]
                total_ignored += 1
            elif current_id_from:
                raise ValueError(
                    "Expected first array to have the same value as from_param: "
                    f"current_id_from: {current_id_from}; but was: {current_result.data[0].id}"
                )

            current_id_from = current_result.data[-1].id
            result.data.extend(current_result.data)
            result.total_count += len(current_result.data)
            if len(current_result.data) < chunk_limit - total_ignored:
                # the trader doesn't have any more orders history
                return result
            if result.total_count > len(current_result.data) and sleep_delay:
                # we don't want to sleep after 1 request only
                await asyncio.sleep(sleep_delay)

    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(self, payload=None, needs_auth: bool = False) -> dict:
        the_timestamp = int(time.time() * 1000)
        the_headers = {
            # "Host": self.blofin_api_base_host,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": self.origin_header,
            "X-Tz": self.timezone,
            "Fp-Request-Id": f"{the_timestamp}.n1fDrN",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": self.user_agent,
            "Connection": "close",
            "appsiteid": "0",
        }

        if self.x_requested_with:
            the_headers["X-Requested-With"] = self.x_requested_with

        if needs_auth:
            the_headers["Authorization"] = f"Bearer {self.authorization_token}"
        return the_headers

    def read_from_session_file(self, file_path: str) -> None:
        """
        Reads from session file; if it doesn't exist, creates it.
        """
        # check if path exists
        target_path = Path(file_path)
        if not target_path.exists():
            return self._save_session_file(file_path=file_path)

        aes = AESCipher(key=f"bf_{self.account_name}_bf", fav_letter=self._fav_letter)
        content = aes.decrypt(target_path.read_text()).decode("utf-8")
        json_data: dict = json.loads(content)

        self.authorization_token = json_data.get(
            "authorization_token",
            self.authorization_token,
        )
        self.timezone = json_data.get("timezone", self.timezone)
        self.user_agent = json_data.get("user_agent", self.user_agent)

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """

        json_data = {
            "authorization_token": self.authorization_token,
            "timezone": self.timezone,
            "user_agent": self.user_agent,
        }
        aes = AESCipher(key=f"bf_{self.account_name}_bf", fav_letter=self._fav_letter)
        target_path = Path(file_path)
        if not target_path.exists():
            target_path.mkdir(parents=True)
        target_path.write_text(aes.encrypt(json.dumps(json_data)))

    # endregion
    ###########################################################
    # region unified methods
    async def get_unified_trader_positions(
        self,
        uid: int | str,
    ) -> UnifiedTraderPositions:
        result = await self.get_copy_trader_all_order_list(
            uid=uid,
        )
        unified_result = UnifiedTraderPositions()
        unified_result.positions = []
        for position in result.data:
            unified_pos = UnifiedPositionInfo()
            unified_pos.position_id = position.id or position.order_id
            unified_pos.position_pnl = position.real_pnl or position.pnl
            unified_pos.position_side = (
                "LONG" if position.order_side in ("LONG", "BUY") else "SHORT"
            )
            unified_pos.margin_mode = position.margin_mode
            unified_pos.position_leverage = Decimal(position.leverage)
            unified_pos.position_pair = position.symbol.replace("-", "/")
            unified_pos.open_time = dt_from_ts(position.open_time)
            unified_pos.open_price = position.avg_open_price
            unified_pos.open_price_unit = position.symbol.split("-")[-1]
            unified_pos.initial_margin = position.get_initial_margin()
            unified_result.positions.append(unified_pos)

        return unified_result

    async def get_unified_trader_info(
        self,
        uid: int | str,
    ) -> UnifiedTraderInfo:
        info_resp = await self.get_copy_trader_info(
            uid=uid,
        )
        info = info_resp.data
        unified_info = UnifiedTraderInfo()
        unified_info.trader_id = info.uid
        unified_info.trader_name = info.nick_name
        unified_info.trader_url = f"{BASE_PROFILE_URL}{info.uid}"
        unified_info.win_rate = info.win_rate

        return unified_info

    # endregion
    ###########################################################
