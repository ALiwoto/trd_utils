"""
BxUltra exchange subclass
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import logging
import gzip
from urllib.parse import urlencode
import uuid

import httpx

import time
from pathlib import Path

import websockets
import websockets.asyncio
import websockets.asyncio.client
import websockets.asyncio.connection

from trd_utils.exchanges.base_types import (
    UnifiedPositionInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.exchanges.bx_ultra.bx_utils import do_ultra_ss
from trd_utils.exchanges.bx_ultra.bx_types import (
    AssetsInfoResponse,
    ContractConfigResponse,
    ContractOrdersHistoryResponse,
    ContractsListResponse,
    CopyTraderFuturesStatsResponse,
    CopyTraderResumeResponse,
    CopyTraderTradePositionsResponse,
    CreateOrderDelegationResponse,
    HintListResponse,
    HomePageResponse,
    HotSearchResponse,
    QuotationRankResponse,
    SearchCopyTraderCondition,
    SearchCopyTradersResponse,
    SingleCandleInfo,
    UserFavoriteQuotationResponse,
    ZenDeskABStatusResponse,
    ZenDeskAuthResponse,
    ZoneModuleListResponse,
)
from trd_utils.cipher import AESCipher

from trd_utils.exchanges.errors import ExchangeError
from trd_utils.exchanges.exchange_base import ExchangeBase, JWTManager
from trd_utils.exchanges.price_fetcher import IPriceFetcher

PLATFORM_ID_ANDROID = "10"
PLATFORM_ID_WEB = "30"
PLATFORM_ID_TG = "100"

ANDROID_DEVICE_BRAND = "SM-N976N"
WEB_DEVICE_BRAND = "Windows 10_Chrome_127.0.0.0"
EDGE_DEVICE_BRAND = "Windows 10_Edge_131.0.0.0"

ANDROID_APP_VERSION = "4.28.3"
WEB_APP_VERSION = "4.78.12"
TG_APP_VERSION = "5.0.15"

ACCEPT_ENCODING_HEADER = "gzip, deflate, br, zstd"
BASE_PROFILE_URL = "https://bingx.com/en/CopyTrading/"

logger = logging.getLogger(__name__)

# The cache in which we will be storing the api identities.
# The key of this dict is uid (long user identifier), to api-identity.
# Why is this a global variable, and not a class attribute? because as far as
# I've observed, api-identities in bx (unlike Telegram's access-hashes) are not
# specific to the current session that is fetching them,
user_api_identity_cache: dict[int, int] = {}


class BXUltraClient(ExchangeBase, IPriceFetcher):
    ###########################################################
    # region client parameters
    we_api_base_host: str = "\u0061pi-\u0061pp.w\u0065-\u0061pi.com"
    we_api_base_url: str = "https://\u0061pi-\u0061pp.w\u0065-\u0061pi.com/\u0061pi"
    ws_we_api_base_url: str = "wss://ws-market-swap.w\u0065-\u0061pi.com/ws"
    original_base_host: str = "https://\u0062ing\u0078.co\u006d"
    qq_os_base_host: str = "https://\u0061pi-\u0061pp.\u0071\u0071-os.com"
    qq_os_base_url: str = "https://\u0061pi-\u0061pp.\u0071\u0071-os.com/\u0061pi"

    origin_header: str = "https://\u0062ing\u0078.co\u006d"
    app_id: str = "30004"
    main_app_id: str = "10009"
    trade_env: str = "real"
    timezone: str = "3"
    os_version: str = "7.1.2"
    device_brand: str = "SM-N976N"
    platform_lang: str = "en"
    sys_lang: str = "en"

    # a dict that maps "BTC/USDT" to it single candle info.
    __last_candle_storage: dict = None
    __last_candle_lock: asyncio.Lock = None
    # endregion
    ###########################################################
    # region client constructor
    def __init__(
        self,
        account_name: str = "default",
        platform_id: str = PLATFORM_ID_ANDROID,
        device_brand: str = ANDROID_DEVICE_BRAND,
        app_version: str = ANDROID_APP_VERSION,
        http_verify: bool = True,
        fav_letter: str = "^",
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
        self.platform_id = platform_id
        self.device_brand = device_brand
        self.app_version = app_version
        self._fav_letter = fav_letter
        self.sessions_dir = sessions_dir
        self.exchange_name = "\u0062ing\u0078"

        super().__init__()
        self.read_from_session_file(
            file_path=f"{self.sessions_dir}/{self.account_name}.bx"
        )
        self.__last_candle_storage = {}
        self.__last_candle_lock = asyncio.Lock()

    # endregion
    ###########################################################
    # region api/coin/v1
    async def get_zone_module_info(
        self,
        only_one_position: int = 0,
        biz_type: int = 10,
    ) -> ZoneModuleListResponse:
        """
        Fetches and returns zone module info from the API.
        Available zones are: All, Forex, Indices, MEME, Elon-inspired,
        Innovation, AI Agent, BTC Ecosystem, TON Ecosystem, Commodities,
        GameFi, Fan Tokens , Layer1 & Layer2, SOL Ecosystem, RWA, LST, DePin, AI
        """
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        return await self.invoke_get(
            f"{self.we_api_base_url}/coin/v1/zone/module-info",
            headers=headers,
            params=params,
            model_type=ZoneModuleListResponse,
        )

    async def get_user_favorite_quotation(
        self,
        only_one_position: int = 0,
        biz_type: int = 1,
    ) -> UserFavoriteQuotationResponse:
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        return await self.invoke_get(
            f"{self.we_api_base_url}/coin/v1/user/favorite/quotation",
            headers=headers,
            params=params,
            model_type=UserFavoriteQuotationResponse,
        )

    async def get_quotation_rank(
        self,
        only_one_position: int = 0,
        order_flag: int = 0,
    ) -> QuotationRankResponse:
        params = {
            "orderFlag": f"{order_flag}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        return await self.invoke_get(
            f"{self.we_api_base_url}/coin/v1/rank/quotation-rank",
            headers=headers,
            params=params,
            model_type=QuotationRankResponse,
        )

    async def get_hot_search(
        self,
        only_one_position: int = 0,
        biz_type: int = 30,
    ) -> HotSearchResponse:
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        return await self.invoke_get(
            f"{self.we_api_base_url}/coin/v1/quotation/hot-search",
            headers=headers,
            params=params,
            model_type=HotSearchResponse,
        )

    async def get_homepage(
        self,
        only_one_position: int = 0,
        biz_type: int = 30,
    ) -> HomePageResponse:
        params = {
            "biz-type": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        return await self.invoke_get(
            f"{self.we_api_base_url}/coin/v1/discovery/homepage",
            headers=headers,
            params=params,
            model_type=HomePageResponse,
        )

    # endregion
    ###########################################################
    # region customer
    async def get_zendesk_ab_status(self) -> ZenDeskABStatusResponse:
        headers = self.get_headers()
        return await self.invoke_get(
            f"{self.we_api_base_url}/customer/v1/zendesk/ab-status",
            headers=headers,
            model_type=ZenDeskABStatusResponse,
        )

    async def do_zendesk_auth(self) -> ZenDeskAuthResponse:
        headers = self.get_headers(needs_auth=True)
        return await self.invoke_get(
            f"{self.we_api_base_url}/customer/v1/zendesk/auth/jwt",
            headers=headers,
            model_type=ZenDeskAuthResponse,
        )

    async def re_authorize_user(self) -> bool:
        result = await self.do_zendesk_auth()
        if not result.data.jwt:
            return False

        self.authorization_token = result.data.jwt
        self._save_session_file(file_path=f"{self.sessions_dir}/{self.account_name}.bx")
        return True

    # endregion
    ###########################################################
    # region platform-tool
    async def get_hint_list(self) -> HintListResponse:
        headers = self.get_headers()
        return await self.invoke_get(
            f"{self.we_api_base_url}/platform-tool/v1/hint/list",
            headers=headers,
            model_type=HintListResponse,
        )

    # endregion
    ###########################################################
    # region asset-manager
    async def get_assets_info(self) -> AssetsInfoResponse:
        headers = self.get_headers(needs_auth=True)
        return await self.invoke_get(
            f"{self.we_api_base_url}/asset-manager/v1/assets/account-total-overview",
            headers=headers,
            model_type=AssetsInfoResponse,
        )

    # endregion
    ###########################################################
    # region ws-subscribes
    async def do_price_subscribe(self) -> None:
        """
        Subscribes to the price changes coming from the exchange.
        NOTE: This method DOES NOT return. you should do create_task
            for it.
        """
        params = {
            "platformid": self.platform_id,
            "app_version": self.app_version,
            "x-router-tag": self.x_router_tag,
            "lang": self.platform_lang,
            "device_id": self.device_id,
            "channel": self.channel_header,
            "device_brand": self.device_brand,
            "traceId": self.trace_id,
        }
        url = f"{self.ws_we_api_base_url}?{urlencode(params, doseq=True)}"
        while True:
            try:
                await self._do_price_ws(
                    url=url,
                )
            except asyncio.CancelledError:
                return
            except Exception as ex:
                err_str = f"{ex}"
                if err_str.find("Event loop is closed") != -1:
                    # just return
                    return

                logger.warning(f"error at _do_price_ws: {err_str}")
                await asyncio.sleep(1)

    async def _do_price_ws(self, url: str):
        async with websockets.connect(url, ping_interval=None) as ws:
            await self._internal_lock.acquire()
            self.price_ws_connection = ws
            self._internal_lock.release()

            await ws.send(json.dumps({
                "dataType": "swap.market.v2.contracts",
                "id": uuid.uuid4().hex,
                "reqType": "sub",
            }))
            async for msg in ws:
                try:
                    decompressed_message = gzip.decompress(msg)
                    str_msg = decompressed_message.decode("utf-8")
                    await self._handle_price_ws_msg(
                        str_msg=str_msg,
                    )
                except Exception as ex:
                    logger.info(f"failed to handle ws message from exchange: {msg}; {ex}")

    async def _handle_price_ws_msg(self, str_msg: str):
        if str_msg.lower() == "ping":
            await self.price_ws_connection.send("Pong")
            return

        data: dict = json.loads(str_msg, parse_float=Decimal)
        if not isinstance(data, dict):
            logger.warning(f"invalid data instance: {type(data)}")
            return

        if data.get("code", 0) == 0 and data.get("data", None) is None:
            # it's all fine
            return

        if data.get("ping", None):
            target_id = data["ping"]
            target_time = data.get(
                "time",
                datetime.now(
                    timezone(timedelta(hours=8))
                ).isoformat(timespec="seconds")
            )
            await self.price_ws_connection.send(json.dumps({
                "pong": target_id,
                "time": target_time,
            }))
            return

        inner_data = data.get("data", None)
        if isinstance(inner_data, dict):
            if data.get("dataType", None) == "swap.market.v2.contracts":
                list_data = inner_data.get("l", None)
                await self.__last_candle_lock.acquire()
                for current in list_data:
                    info = SingleCandleInfo.deserialize_short(current)
                    if info:
                        self.__last_candle_storage[info.pair.lower()] = info
                self.__last_candle_lock.release()
            return

        logger.info(f"we got some unknown data: {data}")
    
    async def get_last_candle(self, pair: str) -> SingleCandleInfo:
        """
        Returns the last candle's info in this exchange.
        This method is safe to be called ONLY from the exact same thread
        that the loop is currently operating on.
        """
        await self.__last_candle_lock.acquire()
        info = self.__last_candle_storage.get(pair.lower())
        self.__last_candle_lock.release()
        return info
    
    # endregion
    ###########################################################
    # region contract
    async def get_contract_config(
        self,
        fund_type: int, # e.g. 1
        coin_name: str, # e.g. "SOL"
        valuation_name: str, # e.g. "USDT"
        margin_coin_name: str, # e.g. "USDT"
    ) -> ContractConfigResponse:
        params = {
            "fundType": f"{fund_type}",
            "coinName": f"{coin_name}",
            "valuationName": f"{valuation_name}",
            "marginCoinName": f"{margin_coin_name}",
        }
        headers = self.get_headers(
            payload=params,
        )
        return await self.invoke_get(
            # "https://bingx.com/api/v2/contract/config",
            f"{self.qq_os_base_url}/v2/contract/config",
            headers=headers,
            params=params,
            model_type=CopyTraderTradePositionsResponse,
        )
        
    async def get_contract_list(
        self,
        quotation_coin_id: int = -1,
        margin_type: int = -1,
        page_size: int = 20,
        page_id: int = 0,
        margin_coin_name: str = "",
        create_type: str = -1,
    ) -> ContractsListResponse:
        params = {
            "quotationCoinId": f"{quotation_coin_id}",
            "marginType": f"{margin_type}",
            "pageSize": f"{page_size}",
            "pageId": f"{page_id}",
            "createType": f"{create_type}",
        }
        if margin_coin_name:
            params["marginCoinName"] = margin_coin_name
        headers = self.get_headers(params, needs_auth=True)
        return await self.invoke_get(
            f"{self.we_api_base_url}/v4/contract/order/hold",
            headers=headers,
            params=params,
            model_type=ContractsListResponse,
        )

    async def get_contract_order_history(
        self,
        fund_type: int = 1,
        paging_size: int = 10,
        page_id: int = 0,
        from_order_no: int = 0,
        margin_coin_name: str = "USDT",
        margin_type: int = 0,
    ) -> ContractOrdersHistoryResponse:
        params = {
            "fundType": f"{fund_type}",
            "pagingSize": f"{paging_size}",
            "pageId": f"{page_id}",
            "marginCoinName": margin_coin_name,
            "marginType": f"{margin_type}",
        }
        if from_order_no:
            params["fromOrderNo"] = f"{from_order_no}"

        headers = self.get_headers(params, needs_auth=True)
        return await self.invoke_get(
            f"{self.we_api_base_url}/v2/contract/order/history",
            headers=headers,
            params=params,
            model_type=ContractOrdersHistoryResponse,
        )

    async def get_today_contract_earnings(
        self,
        margin_coin_name: str = "USDT",
        page_size: int = 10,
        max_total_size: int = 500,
        delay_per_fetch: float = 1.0,
    ) -> Decimal:
        """
        Fetches today's earnings from the contract orders.
        NOTE: This method is a bit slow due to the API rate limiting.
        NOTE: If the user has not opened ANY contract orders today,
            this method will return None.
        """
        return await self._get_period_contract_earnings(
            period="day",
            margin_coin_name=margin_coin_name,
            page_size=page_size,
            max_total_size=max_total_size,
            delay_per_fetch=delay_per_fetch,
        )

    async def get_this_week_contract_earnings(
        self,
        margin_coin_name: str = "USDT",
        page_size: int = 10,
        max_total_size: int = 500,
        delay_per_fetch: float = 1.0,
    ) -> Decimal:
        """
        Fetches this week's earnings from the contract orders.
        NOTE: This method is a bit slow due to the API rate limiting.
        NOTE: If the user has not opened ANY contract orders this week,
            this method will return None.
        """
        return await self._get_period_contract_earnings(
            period="week",
            margin_coin_name=margin_coin_name,
            page_size=page_size,
            max_total_size=max_total_size,
            delay_per_fetch=delay_per_fetch,
        )

    async def get_this_month_contract_earnings(
        self,
        margin_coin_name: str = "USDT",
        page_size: int = 10,
        max_total_size: int = 500,
        delay_per_fetch: float = 1.0,
    ) -> Decimal:
        """
        Fetches this month's earnings from the contract orders.
        NOTE: This method is a bit slow due to the API rate limiting.
        NOTE: If the user has not opened ANY contract orders this week,
            this method will return None.
        """
        return await self._get_period_contract_earnings(
            period="month",
            margin_coin_name=margin_coin_name,
            page_size=page_size,
            max_total_size=max_total_size,
            delay_per_fetch=delay_per_fetch,
        )

    async def _get_period_contract_earnings(
        self,
        period: str,
        margin_coin_name: str = "USDT",
        page_size: int = 10,
        max_total_size: int = 500,
        delay_per_fetch: float = 1.0,
    ) -> Decimal:
        total_fetched = 0
        total_earnings = Decimal("0.00")
        has_earned_any = False
        while total_fetched < max_total_size:
            current_page = total_fetched // page_size
            result = await self.get_contract_order_history(
                page_id=current_page,
                paging_size=page_size,
                margin_coin_name=margin_coin_name,
            )
            if period == "day":
                temp_earnings = result.get_today_earnings()
            elif period == "week":
                temp_earnings = result.get_this_week_earnings()
            elif period == "month":
                temp_earnings = result.get_this_month_earnings()
            if temp_earnings is None:
                # all ended
                break
            total_earnings += temp_earnings
            has_earned_any = True
            total_fetched += page_size
            if result.get_orders_len() < page_size:
                break
            await asyncio.sleep(delay_per_fetch)

        if not has_earned_any:
            return None
        return total_earnings

    # endregion
    ###########################################################
    # region contract delegation
    async def create_order_delegation(
        self,
        balance_direction: int,  # e.g. 1
        delegate_price: Decimal,  # e.g. 107414.70
        fund_type: int,  # # e.g. 1
        large_spread_rate: int,  # e.g. 0
        lever_times: int,  # e.g. 5
        margin: int,  # e.g. 5
        margin_coin_name: str,  # e.g. "USDT"
        market_factor: int,  # e.g. 1
        order_type: int,  # e.g. 0
        price: Decimal,  # the current price of the market??
        stop_loss_rate: int,  # e.g. -1
        stop_profit_rate: int,  # e.g. -1
        quotation_coin_id: int,  # e.g. 1
        spread_rate: float,  # something very low. e.g. 0.00003481
        stop_loss_price: float,  # e.g. -1
        stop_profit_price: float,  # e.g. -1
        up_ratio: Decimal,  # e.g. 0.5
    ) -> CreateOrderDelegationResponse:
        payload = {
            "balanceDirection": balance_direction,
            "delegatePrice": f"{delegate_price}",
            "fundType": fund_type,
            "largeSpreadRate": large_spread_rate or 0,
            "leverTimes": lever_times or 1,
            "margin": margin,
            "marginCoinName": margin_coin_name or "USDT",
            "marketFactor": market_factor or 1,
            "orderType": f"{order_type or 0}",
            "price": float(price), # e.g. 107161.27
            "profitLossRateDto": {
                "stopProfitRate": stop_profit_rate or -1,
                "stopLossRate": stop_loss_rate or -1,
            },
            "quotationCoinId": quotation_coin_id or 1,
            "spreadRate": float(spread_rate) or 0.00003481,
            "stopLossPrice": stop_loss_price or -1,
            "stopProfitPrice": stop_profit_price or -1,
            "upRatio": f"{0.5 if up_ratio is None else up_ratio}",
        }
        headers = self.get_headers(
            needs_auth=True,
            payload=payload,
        )
        return await self.invoke_post(
            f"{self.we_api_base_url}/v2/contract/order/delegation",
            headers=headers,
            content=payload,
            model_type=CreateOrderDelegationResponse,
        )
    # endregion
    ###########################################################
    # region copy-trade-facade
    async def get_copy_trader_positions(
        self,
        uid: int | str,
        api_identity: str,
        page_size: int = 20,
        page_id: int = 0,
        copy_trade_label_type: int = 1,
    ) -> CopyTraderTradePositionsResponse:
        params = {
            "uid": f"{uid}",
            "apiIdentity": f"{api_identity}",
            "pageSize": f"{page_size}",
            "pageId": f"{page_id}",
            "copyTradeLabelType": f"{copy_trade_label_type}",
        }
        headers = self.get_headers(params)
        return await self.invoke_get(
            f"{self.we_api_base_url}/copy-trade-facade/v2/real/trader/positions",
            headers=headers,
            params=params,
            model_type=CopyTraderTradePositionsResponse,
        )

    async def search_copy_traders(
        self,
        exchange_id: int = 2,
        nick_name: str = "",
        conditions: list[SearchCopyTraderCondition] = None,
        page_id: int = 0,
        page_size: int = 20,
        sort: str = "comprehensive",
        order: str = "desc",
    ) -> SearchCopyTradersResponse:
        params = {
            "pageId": f"{page_id}",
            "pageSize": f"{page_size}",
            "sort": sort,
            "order": order,
        }
        if conditions is None:
            conditions = [
                {"key": "exchangeId", "selected": "2", "type": "singleSelect"}
            ]
        else:
            conditions = [x.to_dict() for x in conditions]

        payload = {
            "conditions": conditions,
            "exchangeId": f"{exchange_id}",
            "nickName": nick_name,
        }
        headers = self.get_headers(payload)
        return await self.invoke_post(
            f"{self.we_api_base_url}/v6/copy-trade/search/search",
            headers=headers,
            params=params,
            content=payload,
            model_type=SearchCopyTradersResponse,
        )

    async def get_copy_trader_futures_stats(
        self,
        uid: int | str,
        api_identity: str,
    ) -> CopyTraderFuturesStatsResponse:
        """
        Returns futures statistics of a certain trader.
        If you do not have the api_identity parameter, please first invoke
        get_copy_trader_resume method and get it from there.
        """
        params = {
            "uid": f"{uid}",
            "apiIdentity": f"{api_identity}",
        }
        headers = self.get_headers(params)
        return await self.invoke_get(
            f"{self.we_api_base_url}/copy-trade-facade/v4/trader/account/futures/stat",
            headers=headers,
            params=params,
            model_type=CopyTraderFuturesStatsResponse,
        )

    async def get_copy_trader_resume(
        self,
        uid: int | str,
    ) -> CopyTraderResumeResponse:
        params = {
            "uid": f"{uid}",
        }
        headers = self.get_headers(params)
        return await self.invoke_get(
            f"{self.we_api_base_url}/copy-trade-facade/v1/trader/resume",
            headers=headers,
            params=params,
            model_type=CopyTraderResumeResponse,
        )

    async def get_trader_api_identity(
        self,
        uid: int | str,
        sub_account_filter: str = "futures",
    ) -> int | str:
        global user_api_identity_cache
        api_identity = user_api_identity_cache.get(uid, None)
        if not api_identity:
            resume = await self.get_copy_trader_resume(
                uid=uid,
            )
            api_identity = resume.data.api_identity
            if not api_identity:
                # second try: try to use one of the sub-accounts' identity
                api_identity = resume.data.get_account_identity_by_filter(sub_account_filter)

            # maybe also try to fetch it in other ways later?
            # ...
            user_api_identity_cache[uid] = api_identity
        return api_identity

    # endregion
    ###########################################################
    # region welfare
    async def do_daily_check_in(self):
        headers = self.get_headers(needs_auth=True)
        return await self.invoke_post(
            f"{self.original_base_host}/api/act-operation/v1/welfare/sign-in/do",
            headers=headers,
            content="",
            model_type=None,
        )

    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(self, payload=None, needs_auth: bool = False) -> dict:
        the_timestamp = int(time.time() * 1000)
        the_headers = {
            "Host": self.we_api_base_host,
            "Content-Type": "application/json",
            "Mainappid": self.main_app_id,
            "Accept": "application/json",
            "Origin": self.origin_header,
            "Traceid": self.trace_id,
            "App_version": self.app_version,
            "Platformid": self.platform_id,
            "Device_id": self.device_id,
            "Device_brand": self.device_brand,
            "Channel": self.channel_header,
            "Appid": self.app_id,
            "Trade_env": self.trade_env,
            "Timezone": self.timezone,
            "Lang": self.platform_lang,
            "Syslang": self.sys_lang,
            "Sign": do_ultra_ss(
                e_param=None,
                se_param=None,
                le_param=None,
                timestamp=the_timestamp,
                trace_id=self.trace_id,
                device_id=self.device_id,
                platform_id=self.platform_id,
                app_version=self.app_version,
                payload_data=payload,
            ),
            "Timestamp": f"{the_timestamp}",
            "Accept-Encoding": ACCEPT_ENCODING_HEADER,
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

        aes = AESCipher(key=f"bx_{self.account_name}_bx", fav_letter=self._fav_letter)
        content = aes.decrypt(target_path.read_text()).decode("utf-8")
        json_data: dict = json.loads(content)

        self.device_id = json_data.get("device_id", self.device_id)
        self.trace_id = json_data.get("trace_id", self.trace_id)
        self.app_version = json_data.get("app_version", self.app_version)
        self.platform_id = json_data.get("platform_id", self.platform_id)
        self.install_channel = json_data.get("install_channel", self.install_channel)
        self.channel_header = json_data.get("channel_header", self.channel_header)
        self.authorization_token = json_data.get(
            "authorization_token", self.authorization_token
        )
        if self.authorization_token:
            self.jwt_manager = JWTManager(self.jwt_manager)
        self.app_id = json_data.get("app_id", self.app_id)
        self.trade_env = json_data.get("trade_env", self.trade_env)
        self.timezone = json_data.get("timezone", self.timezone)
        self.os_version = json_data.get("os_version", self.os_version)
        self.device_brand = json_data.get("device_brand", self.device_brand)
        self.platform_lang = json_data.get("platform_lang", self.platform_lang)
        self.sys_lang = json_data.get("sys_lang", self.sys_lang)
        self.user_agent = json_data.get("user_agent", self.user_agent)

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """
        if file_path is None:
            file_path = f"{self.sessions_dir}/{self.account_name}.bx"

        if not self.device_id:
            self.device_id = uuid.uuid4().hex.replace("-", "") + "##"

        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex.replace("-", "")

        json_data = {
            "device_id": self.device_id,
            "trace_id": self.trace_id,
            "app_version": self.app_version,
            "platform_id": self.platform_id,
            "install_channel": self.install_channel,
            "channel_header": self.channel_header,
            "authorization_token": self.authorization_token,
            "app_id": self.app_id,
            "trade_env": self.trade_env,
            "timezone": self.timezone,
            "os_version": self.os_version,
            "device_brand": self.device_brand,
            "platform_lang": self.platform_lang,
            "sys_lang": self.sys_lang,
            "user_agent": self.user_agent,
        }
        aes = AESCipher(key=f"bx_{self.account_name}_bx", fav_letter=self._fav_letter)
        target_path = Path(file_path)
        if not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.touch()
        target_path.write_text(aes.encrypt(json.dumps(json_data)))

    # endregion
    ###########################################################
    # region unified methods

    async def get_unified_trader_positions(
        self,
        uid: int | str,
        api_identity: int | str | None = None,
        sub_account_filter: str = "futures",
    ) -> UnifiedTraderPositions:
        if not api_identity:
            api_identity = await self.get_trader_api_identity(
                uid=uid,
                sub_account_filter=sub_account_filter,
            )
        
        if not api_identity:
            raise ValueError(f"Failed to fetch api_identity for user {uid}")

        result = await self.get_copy_trader_positions(
            uid=uid,
            api_identity=api_identity,
            page_size=50,  # TODO: make this dynamic I guess...
        )
        if not result.data:
            if result.msg:
                raise ExchangeError(result.msg)
            raise ExchangeError(
                f"Unknown error happened while fetching positions of {uid}, "
                f"code: {result.code}"
            )
        if result.data.hide == 0 and not result.data.positions:
            # TODO: do proper exceptions here...
            raise ValueError("The trader has made their positions hidden")
        unified_result = UnifiedTraderPositions()
        unified_result.positions = []
        for position in result.data.positions:
            unified_pos = UnifiedPositionInfo()
            unified_pos.position_id = position.position_no
            unified_pos.position_pnl = position.unrealized_pnl
            unified_pos.position_side = position.position_side
            unified_pos.margin_mode = "isolated"  # TODO: fix this
            unified_pos.position_leverage = position.leverage
            unified_pos.position_pair = position.symbol.replace("-", "/")
            unified_pos.open_time = None  # TODO: do something for this?
            unified_pos.open_price = position.avg_price
            unified_pos.open_price_unit = (
                position.valuation_coin_name or position.symbol.split("-")[-1]
            )  # TODO

            last_candle = await self.get_last_candle(unified_pos.position_pair)
            if last_candle:
                unified_pos.last_price = last_candle.close_price
                unified_pos.last_volume = last_candle.quote_volume

            unified_result.positions.append(unified_pos)

        return unified_result

    async def get_unified_trader_info(
        self,
        uid: int | str,
    ) -> UnifiedTraderInfo:
        resume_resp = await self.get_copy_trader_resume(
            uid=uid,
        )
        if resume_resp.code != 0 and not resume_resp.data:
            if resume_resp.msg:
                raise ValueError(f"got error from API: {resume_resp.msg}")
            raise ValueError(
                f"got unknown error from bx API while fetching resume for {uid}"
            )

        resume = resume_resp.data
        api_identity = resume.api_identity

        info_resp = await self.get_copy_trader_futures_stats(
            uid=uid,
            api_identity=api_identity,
        )
        info = info_resp.data
        unified_info = UnifiedTraderInfo()
        unified_info.trader_id = resume.trader_info.uid
        unified_info.trader_name = resume.trader_info.nick_name
        unified_info.trader_url = f"{BASE_PROFILE_URL}{uid}"
        unified_info.win_rate = Decimal(info.win_rate.rstrip("%")) / 100

        return unified_info

    # endregion
    ###########################################################
