from datetime import datetime
from decimal import Decimal
import asyncio
import logging
import httpx
import pytz

from trd_utils.exchanges.base_types import (
    UnifiedFuturesMarketInfo,
    UnifiedPositionInfo,
    UnifiedSingleFutureMarketInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.exchanges.binance.binance_types import (
    BinanceLeaderboardResponse,
    BinanceLeaderboardBaseInfoResponse,
    BinanceTicker24h,
    BinancePremiumIndex,
)

logger = logging.getLogger(__name__)

BASE_LEADERBOARD_PROFILE_URL = (
    "https://www.binance.com/en/futures-activity/leaderboard/user/um"
)


class BinanceClient(ExchangeBase):
    ###########################################################
    # region client parameters

    # Public Futures API
    binance_fapi_base_url: str = "https://fapi.binance.com"

    # Internal Web API (for Leaderboard)
    binance_bapi_base_url: str = "https://www.binance.com/bapi/futures"

    default_quote_token: str = "USDT"

    # endregion
    ###########################################################
    # region client constructor
    def __init__(
        self,
        account_name: str = "default",
        http_verify: bool = True,
        read_session_file: bool = False,
        sessions_dir: str = "sessions",
        use_http1: bool = True,
        use_http2: bool = False,
    ):
        # Binance supports HTTP2, but we respect the flags passed
        self.httpx_client = httpx.AsyncClient(
            verify=http_verify,
            http1=use_http1,
            http2=use_http2,
        )
        self.account_name = account_name
        self.sessions_dir = sessions_dir
        self.exchange_name = "binance"

        super().__init__()

        if read_session_file:
            self.read_from_session_file(f"{sessions_dir}/{self.account_name}.bin")

    # endregion
    ###########################################################
    # region info endpoints (Leaderboard & FAPI)

    async def get_leaderboard_positions(
        self,
        encrypted_uid: str,
    ) -> BinanceLeaderboardResponse:
        """
        Fetches positions from the Binance Futures Leaderboard.
        UID must be the 'encryptedUid'.
        """
        payload = {
            "encryptedUid": encrypted_uid,
            "tradeType": "PERPETUAL",
        }
        # BAPI requires headers that look like a web browser
        headers = self.get_headers(needs_browser_simulation=True)

        return await self.invoke_post(
            f"{self.binance_bapi_base_url}/v1/public/future/leaderboard/getOtherPosition",
            headers=headers,
            content=payload,
            model_type=BinanceLeaderboardResponse,
        )

    async def get_leaderboard_base_info(
        self,
        encrypted_uid: str,
    ) -> BinanceLeaderboardBaseInfoResponse:
        payload = {
            "encryptedUid": encrypted_uid,
        }
        headers = self.get_headers(needs_browser_simulation=True)

        return await self.invoke_post(
            f"{self.binance_bapi_base_url}/v2/public/future/leaderboard/getOtherLeaderboardBaseInfo",
            headers=headers,
            content=payload,
            model_type=BinanceLeaderboardBaseInfoResponse,
        )

    async def get_market_tickers(self) -> list[BinanceTicker24h]:
        """
        Fetches 24hr ticker for all symbols from FAPI.
        """
        headers = self.get_headers()
        data = await self.invoke_get(
            f"{self.binance_fapi_base_url}/fapi/v1/ticker/24hr",
            headers=headers,
            model_type=None,  # returns a list, handled below
        )

        if not isinstance(data, list):
            return []

        return [BinanceTicker24h.deserialize(item) for item in data]

    async def get_premium_indices(self) -> list[BinancePremiumIndex]:
        """
        Fetches premium index (includes funding rates) from FAPI.
        """
        headers = self.get_headers()
        data = await self.invoke_get(
            f"{self.binance_fapi_base_url}/fapi/v1/premiumIndex",
            headers=headers,
            model_type=None,  # returns a list, handled below
        )

        if not isinstance(data, list):
            return []

        return [BinancePremiumIndex.deserialize(item) for item in data]

    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(
        self,
        payload=None,
        needs_auth: bool = False,
        needs_browser_simulation: bool = False,
    ) -> dict:
        the_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        if needs_browser_simulation:
            # The internal B-API often rejects standard API or mobile user agents.
            # We simulate a desktop browser here.
            the_headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            the_headers["ClientType"] = "web"
            the_headers["Client-Type"] = "web"
            the_headers["lang"] = "en"

        if self.x_requested_with:
            the_headers["X-Requested-With"] = self.x_requested_with

        # TODO: Implement API Key signature logic here if private endpoints are added later
        # if needs_auth: ...

        return the_headers

    def read_from_session_file(self, file_path: str) -> None:
        # Not strictly needed for public leaderboard scraping, but kept for consistency
        # with the project structure (e.g. loading proxies or optional keys later).
        pass

    def _save_session_file(self, file_path: str) -> None:
        pass

    # endregion
    ###########################################################
    # region unified methods

    async def get_unified_trader_positions(
        self,
        uid: int | str,
        min_margin: Decimal = 0,
    ) -> UnifiedTraderPositions:
        """
        UID must be the encryptedUid (string).
        """
        resp = await self.get_leaderboard_positions(encrypted_uid=str(uid))

        unified_result = UnifiedTraderPositions()
        unified_result.positions = []

        if (
            not resp
            or not resp.success
            or not resp.data
            or not resp.data.other_position_ret_list
        ):
            return unified_result

        for pos in resp.data.other_position_ret_list:
            # Binance Leaderboard usually doesn't provide isolated/cross margin mode info publicly.
            # It also doesn't provide direct margin used, so we estimate it:
            # Margin = (Amount * MarkPrice) / Leverage
            if not pos.mark_price or not pos.leverage:
                continue

            notional_value = abs(pos.amount * pos.mark_price)
            margin_used = (
                notional_value / Decimal(pos.leverage) if pos.leverage > 0 else 0
            )

            if min_margin and margin_used < min_margin:
                continue

            unified_pos = UnifiedPositionInfo()
            unified_pos.position_id = pos.get_position_id(str(uid))
            unified_pos.position_pnl = round(pos.pnl, 3)
            unified_pos.position_side = pos.get_side()
            unified_pos.margin_mode = "cross"  # Default assumption for leaderboard
            unified_pos.position_leverage = Decimal(pos.leverage)
            unified_pos.position_pair = pos.symbol

            # Binance timestamps are in milliseconds
            if pos.update_time_stamp:
                unified_pos.open_time = datetime.fromtimestamp(
                    pos.update_time_stamp / 1000, tz=pytz.UTC
                )

            unified_pos.open_price = pos.entry_price
            unified_pos.open_price_unit = self.default_quote_token
            unified_pos.position_size = abs(pos.amount)
            unified_pos.initial_margin = margin_used
            
            # We can fill current price if we want, but it's optional in base_types
            unified_pos.last_price = pos.mark_price

            unified_result.positions.append(unified_pos)

        return unified_result

    async def get_unified_trader_info(
        self,
        uid: int | str,
    ) -> UnifiedTraderInfo:
        resp = await self.get_leaderboard_base_info(encrypted_uid=str(uid))

        unified_info = UnifiedTraderInfo()
        unified_info.trader_id = str(uid)

        if resp.success and resp.data:
            unified_info.trader_name = resp.data.nick_name
        else:
            # If the request fails or data is hidden, we set a default
            unified_info.trader_name = "Unknown Binance Trader"

        unified_info.trader_url = (
            f"{BASE_LEADERBOARD_PROFILE_URL}?encryptedUid={uid}"
        )
        unified_info.win_rate = None  # Not provided in the base info endpoint

        return unified_info

    async def get_unified_futures_market_info(
        self,
        sort_by: str = "percentage_change_24h",
        descending: bool = True,
        allow_delisted: bool = False,
    ) -> UnifiedFuturesMarketInfo:
        # We fetch tickers and premium indices (for funding rates) in parallel
        tickers_task = self.get_market_tickers()
        premium_index_task = self.get_premium_indices()

        tickers, premium_indices = await asyncio.gather(
            tickers_task, premium_index_task
        )

        # Map funding rates: Symbol -> FundingRate
        funding_map = {p.symbol: p.last_funding_rate for p in premium_indices}

        unified_info = UnifiedFuturesMarketInfo()
        unified_info.sorted_markets = []

        for ticker in tickers:
            symbol = ticker.symbol

            # Parse Base and Quote from the symbol string (e.g. BTCUSDT -> BTC, USDT)
            # Binance Futures symbols are usually {Base}{Quote}.
            base_asset = symbol
            quote_asset = self.default_quote_token
            
            # Basic suffix checking to separate Base and Quote
            if symbol.endswith("USDT"):
                base_asset = symbol[:-4]
                quote_asset = "USDT"
            elif symbol.endswith("USDC"):
                base_asset = symbol[:-4]
                quote_asset = "USDC"
            elif symbol.endswith("BUSD"):
                base_asset = symbol[:-4]
                quote_asset = "BUSD"
            
            current_market = UnifiedSingleFutureMarketInfo()
            current_market.name = base_asset
            current_market.pair = f"{base_asset}/{quote_asset}"
            
            current_market.price = ticker.last_price
            current_market.previous_day_price = ticker.prev_close_price
            current_market.absolute_change_24h = ticker.price_change
            current_market.percentage_change_24h = ticker.price_change_percent
            current_market.funding_rate = funding_map.get(ticker.symbol, Decimal(0))
            current_market.daily_volume = ticker.quote_volume  # Quote Asset Volume
            current_market.open_interest = Decimal(0) 

            unified_info.sorted_markets.append(current_market)

        if not sort_by:
            return unified_info

        def key_fn(market: UnifiedSingleFutureMarketInfo):
            val = getattr(market, sort_by, None)
            if val is None:
                return Decimal("-Infinity") if descending else Decimal("Infinity")
            return val

        unified_info.sorted_markets = sorted(
            unified_info.sorted_markets,
            key=key_fn,
            reverse=descending,
        )
        return unified_info

    # endregion
    ###########################################################

