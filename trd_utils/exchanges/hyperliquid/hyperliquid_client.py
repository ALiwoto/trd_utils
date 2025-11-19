from datetime import datetime
from decimal import Decimal
import json
import logging
import httpx

from pathlib import Path

import pytz

from trd_utils.cipher import AESCipher
from trd_utils.common_utils.wallet_utils import shorten_wallet_address
from trd_utils.exchanges.base_types import (
    UnifiedFuturesMarketInfo,
    UnifiedPositionInfo,
    UnifiedSingleFutureMarketInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.exchanges.hyperliquid.hyperliquid_types import (
    MetaAssetCtxResponse,
    TraderPositionsInfoResponse,
)

logger = logging.getLogger(__name__)

BASE_PROFILE_URL = "https://hypurrscan.io/address/"


class HyperLiquidClient(ExchangeBase):
    ###########################################################
    # region client parameters
    hyperliquid_api_base_host: str = "https://api.hyperliquid.xyz"
    hyperliquid_api_base_url: str = "https://api.hyperliquid.xyz"
    origin_header: str = "app.hyperliquid.xy"
    default_quote_token: str = "USDC"

    # endregion
    ###########################################################
    # region client constructor
    def __init__(
        self,
        account_name: str = "default",
        http_verify: bool = True,
        fav_letter: str = "^",
        read_session_file: bool = False,
        sessions_dir: str = "sessions",
        use_http1: bool = True,
        use_http2: bool = False,
    ):
        # it looks like hyperliquid's api endpoints don't support http2 :(
        self.httpx_client = httpx.AsyncClient(
            verify=http_verify,
            http1=use_http1,
            http2=use_http2,
        )
        self.account_name = account_name
        self._fav_letter = fav_letter
        self.sessions_dir = sessions_dir
        self.exchange_name = "hyperliquid"

        super().__init__()

        if read_session_file:
            self.read_from_session_file(f"{sessions_dir}/{self.account_name}.hl")

    # endregion
    ###########################################################
    # region info endpoints
    async def get_trader_positions_info(
        self,
        uid: int | str,
    ) -> TraderPositionsInfoResponse:
        payload = {
            "type": "clearinghouseState",
            "user": f"{uid}",
        }
        headers = self.get_headers()
        return await self.invoke_post(
            f"{self.hyperliquid_api_base_host}/info",
            headers=headers,
            content=payload,
            model_type=TraderPositionsInfoResponse,
        )

    async def get_meta_asset_ctx_info(
        self,
        allow_delisted: bool = False,
    ) -> MetaAssetCtxResponse:
        payload = {
            "type": "metaAndAssetCtxs",
        }
        headers = self.get_headers()
        data = await self.invoke_post(
            f"{self.hyperliquid_api_base_host}/info",
            headers=headers,
            content=payload,
            model_type=None,  # it has a weird response structure
        )

        return MetaAssetCtxResponse.parse_from_api_resp(
            data=data,
            allow_delisted=allow_delisted,
        )

    # endregion
    ###########################################################
    # region another-thing
    # async def get_another_thing_info(self, uid: int) -> AnotherThingInfoResponse:
    #     payload = {
    #         "uid": uid,
    #     }
    #     headers = self.get_headers()
    #     return await self.invoke_post(
    #         f"{self.hyperliquid_api_base_url}/another-thing/info",
    #         headers=headers,
    #         content=payload,
    #         model_type=CopyTraderInfoResponse,
    #     )

    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(self, payload=None, needs_auth: bool = False) -> dict:
        the_headers = {
            # "Host": self.hyperliquid_api_base_host,
            "Content-Type": "application/json",
            "Accept": "application/json",
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
        self.user_agent = json_data.get("user_agent", self.user_agent)

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """

        json_data = {
            "authorization_token": self.authorization_token,
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
        min_margin: Decimal = 0,
    ) -> UnifiedTraderPositions:
        result = await self.get_trader_positions_info(
            uid=uid,
        )
        unified_result = UnifiedTraderPositions()
        unified_result.positions = []
        for position_container in result.asset_positions:
            position = position_container.position
            if min_margin and (
                not position.margin_used or position.margin_used < min_margin
            ):
                continue

            unified_pos = UnifiedPositionInfo()
            unified_pos.position_id = position.get_position_id()
            unified_pos.position_pnl = round(position.unrealized_pnl, 3)
            unified_pos.position_side = position.get_side()
            unified_pos.margin_mode = position.leverage.type
            unified_pos.position_leverage = Decimal(position.leverage.value)
            unified_pos.position_pair = f"{position.coin}/{self.default_quote_token}"
            unified_pos.open_time = datetime.now(
                pytz.UTC
            )  # hyperliquid doesn't provide this...
            unified_pos.open_price = position.entry_px
            unified_pos.open_price_unit = self.default_quote_token
            unified_pos.position_size = abs(position.szi)
            unified_pos.initial_margin = position.margin_used
            unified_result.positions.append(unified_pos)

        return unified_result

    async def get_unified_trader_info(
        self,
        uid: int | str,
    ) -> UnifiedTraderInfo:
        if not isinstance(uid, str):
            uid = str(uid)
        # sadly hyperliquid doesn't really have an endpoint to fetch information
        # so we have to somehow *fake* these...
        # maybe in future try to find a better way?
        unified_info = UnifiedTraderInfo()
        unified_info.trader_id = uid
        unified_info.trader_name = shorten_wallet_address(uid)
        unified_info.trader_url = f"{BASE_PROFILE_URL}{uid}"
        unified_info.win_rate = None

        return unified_info

    async def get_unified_futures_market_info(
        self,
        sort_by: str = "percentage_change_24h",
        descending: bool = True,
        allow_delisted: bool = False,
    ) -> UnifiedFuturesMarketInfo:
        asset_ctxs = await self.get_meta_asset_ctx_info(
            allow_delisted=allow_delisted,
        )
        unified_info = UnifiedFuturesMarketInfo()
        unified_info.sorted_markets = []

        for current_asset in asset_ctxs.assets:
            current_market = UnifiedSingleFutureMarketInfo()
            current_market.name = current_asset.symbol
            current_market.pair = f"{current_asset.symbol}/{self.default_quote_token}"
            current_market.price = current_asset.mark_px
            current_market.previous_day_price = current_asset.prev_day_px
            current_market.absolute_change_24h = current_asset.change_abs
            current_market.percentage_change_24h = current_asset.change_pct
            current_market.funding_rate = current_asset.funding
            current_market.daily_volume = current_asset.day_ntl_vlm
            current_market.open_interest = current_asset.open_interest
            unified_info.sorted_markets.append(current_market)

        if not sort_by:
            # we won't sort anything
            return unified_info

        def key_fn(market: UnifiedSingleFutureMarketInfo):
            return getattr(market, sort_by, Decimal(0))

        unified_info.sorted_markets = sorted(
            unified_info.sorted_markets,
            key=key_fn,
            reverse=descending,
        )
        return unified_info

    # endregion
    ###########################################################
