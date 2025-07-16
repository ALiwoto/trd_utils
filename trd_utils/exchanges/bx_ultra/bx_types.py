from typing import Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import pytz

from trd_utils.exchanges.errors import ExchangeError
from trd_utils.exchanges.price_fetcher import MinimalCandleInfo
from trd_utils.types_helper import BaseModel

from trd_utils.common_utils.float_utils import (
    as_decimal,
    dec_to_str,
    dec_to_normalize,
)

###########################################################

# region constant variables

ORDER_TYPES_MAP = {
    0: "LONG",
    1: "SHORT",
}

# endregion

###########################################################


# region Common types
class BxApiResponse(BaseModel):
    code: int = None
    timestamp: int = None
    msg: str = None

    def __str__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"

    def __repr__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"


class CoinQuotationInfo(BaseModel):
    name: str = None
    coin_type: int = None
    valuation_coin_name: str = None
    coin_name: str = None
    icon_name: str = None
    slug: str = None
    quotation_id: int = None
    open: Decimal = None
    close: Decimal = None
    weight: int = None
    favorite_flag: Any = None  # unknown
    precision: int = None
    coin_precision: int = None
    valuation_precision: int = None
    market_status: Any = None  # unknown
    trader_scale: Decimal = None
    coin_id: int = None
    valuation_coin_id: int = None
    status: Any = None  # unknown
    open_time: Any = None  # unknown
    open_price: Any = None  # unknown
    high24: Optional[Decimal] = None
    low24: Optional[Decimal] = None
    volume24: Optional[Decimal] = None
    amount24: Optional[Decimal] = None
    market_val: Optional[Decimal] = None
    full_name: str = None
    biz_type: int = None

    def __str__(self):
        return f"{self.coin_name}/{self.valuation_coin_name}; price: {self.close}; vol: {self.market_val}"

    def __repr__(self):
        return f"{self.coin_name}/{self.valuation_coin_name}; price: {self.close}; vol: {self.market_val}"


class ExchangeVo(BaseModel):
    exchange_id: int = None
    exchange_name: str = None
    icon: str = None
    account_enum: str = None
    desc: str = None

    def __str__(self):
        return f"{self.exchange_name} ({self.exchange_id}) - {self.account_enum}"

    def __repr__(self):
        return f"{self.exchange_name} ({self.exchange_id}) - {self.account_enum}"


class OrderLeverInfo(BaseModel):
    lever_times: int = None
    selected: bool = False

    def __str__(self):
        return f"{self.lever_times}x"

    def __repr__(self):
        return self.__str__()


class MarginDisplayInfo(BaseModel):
    margin: Decimal = None
    selected: bool = False


class SysForceVoInfo(BaseModel):
    begin_level: int = None
    end_level: int = None
    adjust_margin_rate: Decimal = None


# endregion

###########################################################

# region ZoneModule types


class ZoneModuleInfo(BaseModel):
    id: int = None
    name: str = None
    quotation_list: list[CoinQuotationInfo] = None
    zone_name: str = None
    weight: int = None
    biz_type: int = None

    def __str__(self):
        return f"{self.name} ({self.zone_name})"

    def __repr__(self):
        return f"{self.name} ({self.zone_name})"


class ZoneModuleListResult(BaseModel):
    zone_module_list: list[ZoneModuleInfo] = None
    biz_type: int = None
    need_channel_type: list[int] = None
    icon_url_prefix: str = None


class ZoneModuleListResponse(BxApiResponse):
    data: ZoneModuleListResult = None


# endregion

###########################################################

# region UserFavorite types


class UserFavoriteQuotationResult(BaseModel):
    usdt_margin_list: list[CoinQuotationInfo] = None
    coin_margin_list: list[CoinQuotationInfo] = None
    swap_list: list[CoinQuotationInfo] = None
    biz_type: int = None
    icon_url_prefix: str = None
    recommend: bool = None


class UserFavoriteQuotationResponse(BxApiResponse):
    data: UserFavoriteQuotationResult = None


# endregion

###########################################################

# region QuotationRank types


class QuotationRankBizItem(BaseModel):
    quotation_list: list[CoinQuotationInfo] = None
    biz_type: int = None
    biz_name: str = None


class QuotationRankItem(BaseModel):
    rank_type: int = None
    rank_name: str = None
    rank_biz_list: list[QuotationRankBizItem] = None


class QuotationRankResult(BaseModel):
    rank_list: list[QuotationRankItem] = None
    icon_prefix: str = None
    icon_url_prefix: str = None
    order_flag: int = None
    show_favorite: bool = None


class QuotationRankResponse(BxApiResponse):
    data: QuotationRankResult = None


# endregion

###########################################################

# region HotSearch types


class HotSearchItem(BaseModel):
    symbol: str = None
    coin_name: str = None
    val_coin_name: str = None
    weight: int = None

    def __str__(self):
        return f"{self.coin_name} ({self.symbol})"

    def __repr__(self):
        return f"{self.coin_name} ({self.symbol})"


class HotSearchResult(BaseModel):
    result: list[HotSearchItem] = None
    hint_ab_test: bool = None
    page_id: int = None
    total: int = None


class HotSearchResponse(BxApiResponse):
    data: HotSearchResult = None

    def __str__(self):
        if not self.data:
            return "HotSearchResponse: No data"

        str_result = "HotSearchResponse: \n"
        for current_item in self.data.result:
            str_result += f" - {current_item}\n"

        return str_result

    def __repr__(self):
        return self.__str__()


# endregion

###########################################################

# region HomePage types


class CoinModuleInfoBase(BaseModel):
    name: str = None
    coin_name: str = None
    icon_name: str = None
    valuation_coin_name: str = None
    open: Decimal = None
    close: Decimal = None
    precision: int = None
    biz_type: int = None
    market_val: Decimal = None
    status: int = None
    open_time: int = None
    open_price: Decimal = None
    full_name: str = None
    amount24: Decimal = None
    global_first_publish: bool = None
    st_tag: int = None


class HomePageModuleIncreaseRankData(CoinModuleInfoBase):
    pass


class HomePageModuleIncreaseRank(BaseModel):
    item_name: str = None
    sub_module_type: int = None
    data: list[HomePageModuleIncreaseRankData] = None


class HomePageModuleHotZoneData(CoinModuleInfoBase):
    zone_desc: str = None
    zone_name: str = None
    zone_id: int = None
    zone_price_rate: Decimal = None


class HomePageModuleHotZone(BaseModel):
    data: list[HomePageModuleHotZoneData] = None


class HomePageModuleRecentHotData(CoinModuleInfoBase):
    pass


class HomePageModuleRecentHot(BaseModel):
    data: list[HomePageModuleRecentHotData] = None


class HomePageModuleGlobalDebutData(CoinModuleInfoBase):
    pass


class HomePageModuleGlobalDebut(BaseModel):
    data: list[HomePageModuleGlobalDebutData] = None


class HomePageModuleMainMarketData(CoinModuleInfoBase):
    pass


class HomePageModuleMainMarket(BaseModel):
    data: list[HomePageModuleMainMarketData] = None


class HomePageModulePreOnlineData(CoinModuleInfoBase):
    pass


class HomePageModulePreOnline(BaseModel):
    data: list[HomePageModulePreOnlineData] = None


class HomePageModuleBannerData(BaseModel):
    banner_title: str = None
    banner_img: str = None
    banner_jump_url: str = None


class HomePageModuleBanner(BaseModel):
    data: list[HomePageModuleBannerData] = None


class HomePageModuleInfo(BaseModel):
    module_type: int = None
    module_name: str = None
    module_desc: str = None
    item_list: list = None

    def _check_module_name(
        self, j_data: dict, module_name: str, module_type: int
    ) -> bool:
        return (
            self.module_name == module_name
            or j_data.get("moduleName", None) == module_name
            or self.module_type == module_type
            or j_data.get("moduleType", None) == module_type
        )

    def _get_item_list_type(self, j_data: dict = None) -> type:
        if not j_data:
            # for more safety
            j_data = {}

        if self._check_module_name(j_data, "PRE_ONLINE", 1):
            return list[HomePageModulePreOnline]

        elif self._check_module_name(j_data, "MAIN_MARKET", 2):
            return list[HomePageModuleMainMarket]

        elif self._check_module_name(j_data, "RECENT_HOT", 3):
            return list[HomePageModuleRecentHot]

        elif self._check_module_name(j_data, "HOT_ZONE", 5):
            return list[HomePageModuleHotZone]

        elif self._check_module_name(j_data, "INCREASE_RANK", 6):
            return list[HomePageModuleIncreaseRank]

        elif self._check_module_name(j_data, "BANNER", 7):
            return list[HomePageModuleBanner]

        elif self._check_module_name(j_data, "GLOBAL_DEBUT", 8):
            return list[HomePageModuleGlobalDebut]

        return None

    def __str__(self):
        return (
            f"{self.module_name} ({self.module_type}): {self.module_desc};"
            + f" {len(self.item_list)} items"
        )

    def __repr__(self):
        return (
            f"{self.module_name} ({self.module_type}): {self.module_desc};"
            + f" {len(self.item_list)} items"
        )


class HomePageResult(BaseModel):
    icon_prefix: str = None
    green_amount_img_prefix: str = None
    red_amount_img_prefix: str = None
    module_list: list[HomePageModuleInfo] = None


class HomePageResponse(BxApiResponse):
    data: HomePageResult = None


# endregion

###########################################################

# region ZenDesk types


class ZenDeskABStatusResult(BaseModel):
    ab_status: int = None


class ZenDeskABStatusResponse(BxApiResponse):
    data: ZenDeskABStatusResult = None


class ZenDeskAuthResult(BaseModel):
    jwt: str = None


class ZenDeskAuthResponse(BxApiResponse):
    data: ZenDeskAuthResult = None


# endregion

###########################################################

# region HintList types


class HintListResult(BaseModel):
    hints: list = None  # unknown


class HintListResponse(BxApiResponse):
    data: HintListResult = None


# endregion

###########################################################

# region CopyTrading types


class CopyTradingSymbolConfigInfo(BaseModel):
    price_precision: int = None
    quantity_precision: int = None


class CopyTraderPositionInfo(BaseModel):
    avg_price: Decimal = None
    coin_name: str = None
    leverage: Decimal = None
    liquidated_price: Decimal = None
    margin: Decimal = None
    mark_price: Decimal = None
    position_earning_rate: Decimal = None
    position_no: int = None
    position_side: str = None
    position_side_and_symbol: str = None
    symbol: str = None
    symbol_config: CopyTradingSymbolConfigInfo = None
    unrealized_pnl: Decimal = None
    valuation_coin_name: str = None
    volume: Decimal = None
    search_result: Optional[bool] = None
    short_position_rate: Decimal = None
    total: int = None

    def __str__(self):
        return (
            f"{self.coin_name} / {self.valuation_coin_name} {self.position_side} "
            + f"{dec_to_str(self.leverage)}x "
            + f"vol: {dec_to_str(self.volume)}; "
            + f"price: {dec_to_normalize(self.avg_price)}; "
            + f"margin: {dec_to_str(self.margin)}; "
            + f"unrealized-PnL: {dec_to_str(self.unrealized_pnl)}; "
            + f"ROI: {dec_to_str((self.position_earning_rate * 100))}%"
        )

    def __repr__(self):
        return self.__str__()


class CopyTraderTradePositionsResult(BaseModel):
    hide: int = None
    long_position_rate: Decimal = None
    page_id: int = None
    positions: list[CopyTraderPositionInfo] = None


class CopyTraderTradePositionsResponse(BxApiResponse):
    data: CopyTraderTradePositionsResult = None


class CopyTraderFuturesStatsResult(BaseModel):
    api_identity: int = None
    dis_play_name: str = None
    icon: str = None
    valid: int = None
    risk_status: int = None
    is_relation: int = None
    copier_status: int = None
    vst_copier_status: int = None
    follower_full: bool = None
    being_invite: bool = None
    str_follower_num: int = None
    equity: str = None
    total_earnings: str = None
    follower_earning: str = None
    max_draw_down: str = None
    str_total_earnings_rate: str = None
    str_recent30_days_rate: str = None
    str_recent7_days_rate: str = None
    str_recent90_days_rate: str = None
    str_recent180_days_rate: str = None
    exchange_vo: ExchangeVo = None
    update_time: datetime = None
    commission_rate: float = None
    risk_level7_days: int = None
    risk_level30_days: int = None
    risk_level90_days: int = None
    risk_level180_days: int = None
    str_acc_follower_num: int = None
    win_rate: str = None
    total_transactions: int = None
    profit_count: int = None
    avg_profit_amount: str = None
    avg_profit_rate: str = None
    loss_count: int = None
    avg_loss_amount: str = None
    avg_loss_rate: str = None
    pnl_rate: str = None
    avg_hold_time: int = None
    weekly_trade_frequency: str = None
    trade_days: int = None
    last_trade_time: datetime = None
    expand: int = None
    recent7_day_follower_num_change: int = None
    recent30_day_follower_num_change: int = None
    recent90_day_follower_num_change: int = None
    recent180_day_follower_num_change: int = None
    latest30_days_median_margin: str = None
    latest30_days_median_lever_times: str = None
    cumulative_profit_loss7_d: float = None
    cumulative_profit_loss30_d: float = None
    cumulative_profit_loss90_d: float = None
    cumulative_profit_loss180_d: float = None
    maximum_draw_down: int = None
    max_draw_down7_d: float = None
    max_draw_down30_d: float = None
    max_draw_down90_d: float = None
    max_draw_down180_d: float = None
    total_position_count: int = None
    profitable_position_count: int = None
    loss_position_count: int = None
    profit_realized_pnl_u: float = None
    loss_realized_pnl_u: float = None
    pnl_rate_u: str = None
    avg_profit: float = None
    avg_loss: float = None
    is_pro: int = None


class CopyTraderFuturesStatsResponse(BxApiResponse):
    data: CopyTraderFuturesStatsResult = None


class CopyTraderInfo(BaseModel):
    nick_name: str = None
    avatar: str = None
    brief: str = None
    uid: int = None
    register_date: datetime = None
    calling_code: str = None
    team_id: int = None
    short_uid: int = None
    identity_type: int = None


class CopyTraderVo(BaseModel):
    audit_status: int = None
    trader_status: int = None
    profit_share_rate: float = None
    trader_role: int = None
    recent_avg_margin: int = None
    min_basic_copy_trade_unit: int = None
    max_basic_copy_trade_unit: int = None
    basic_copy_trade_unit: int = None
    copy_trade_rate_on: bool = None
    trader_protect_status: int = None
    trader_public_recommend_status: int = None
    rank_account_id: int = None
    last_trader_time: datetime = None


class CopyTraderAccountGradeVO(BaseModel):
    uid: int = None
    api_identity: int = None
    trader_grade: int = None
    label: int = None
    uid_and_api: str = None


class CopyTraderSharingAccount(BaseModel):
    category: int = None
    trader: int = None
    api_identity: int = None
    display_name: str = None
    icon: str = None
    valid: int = None
    copier_status: int = None
    vst_copier_status: int = None
    follower_full: bool = None
    copy_trade_account_enum: str = None
    order: int = None
    trader_account_grade_vo: Optional[CopyTraderAccountGradeVO] = None
    hide_info: int = None
    copy_trade_label_type: Optional[int] = None


class CopyTraderResumeResult(BaseModel):
    trader_info: CopyTraderInfo = None
    trader_vo: CopyTraderVo = None
    tags: list = None
    has_new: int = None
    labels: list = None
    has_subscribed: int = None
    fans_num: int = None
    follower_num: int = None
    subscriber_num: int = None
    category: int = None
    api_identity: int = None
    trader_sharing_accounts: list[CopyTraderSharingAccount] = None
    latest30_days_earning_ratio: str = None
    swap_copy_trade_label_type: int = None
    is_pro: int = None

    def get_account_identity_by_filter(self, filter_text: str):
        if not self.trader_sharing_accounts:
            return 0
        
        for current in self.trader_sharing_accounts:
            if current.display_name.lower().find(filter_text) != -1 or \
                current.copy_trade_account_enum.lower().find(filter_text) != -1:
                if current.api_identity:
                    return current.api_identity
        return 0


class CopyTraderResumeResponse(BxApiResponse):
    data: CopyTraderResumeResult = None


# endregion

###########################################################

# region SearchCopyTrading types


class SearchCopyTraderCondition(BaseModel):
    key: str = "exchangeId"
    selected: int = 2
    type: str = "singleSelect"

    def to_dict(self):
        return {
            "key": self.key,
            "selected": f"{self.selected}",
            "type": self.type,
        }


class SearchedTraderChartItem(BaseModel):
    cumulative_pnl_rate: Decimal = None


class SearchedTraderExchangeVoInfo(BaseModel):
    account_enum: str = None
    desc: str = None
    exchange_id: int = None
    exchange_name: str = None
    icon: str = None


class SearchTraderInfoRankStat(BaseModel):
    api_identity: int = None
    avg_hold_time: str = None
    avg_loss_amount: str = None
    avg_loss_rate: str = None
    avg_profit_amount: str = None
    avg_profit_rate: str = None
    being_invite: bool = None
    chart: list[SearchedTraderChartItem] = None  # unknown; list
    copier_status: int = None
    dis_play_name: str = None
    equity: str = None
    exchange_vo: ExchangeVo = None  # unknown
    expand: int = None
    follower_earning: str = None
    follower_full: bool = None
    icon: str = None
    is_pro: bool = None
    is_relation: bool = None
    last_trade_time: str = None
    latest30_days_median_lever_times: str = None
    latest30_days_median_margin: str = None
    loss_count: int = None
    max_draw_down: str = None
    pnl_rate: str = None
    profit_count: int = None
    recent7_day_follower_num_change: int = None
    recent30_day_follower_num_change: int = None
    recent90_day_follower_num_change: int = None
    recent180_day_follower_num_change: int = None
    risk_level7_days: str = None
    risk_level30_days: str = None
    risk_level90_days: str = None
    risk_level180_days: str = None
    risk_status: int = None
    str_acc_follower_num: str = None
    str_follower_num: str = None
    str_recent7_days_rate: str = None
    str_recent30_days_rate: str = None
    str_recent90_days_rate: str = None
    str_recent180_days_rate: str = None
    str_recent180_days_rate: str = None
    str_total_earnings_rate: str = None
    total_earnings: str = None
    total_transactions: int = None
    trade_days: str = None
    update_time: str = None
    valid: int = None
    vst_copier_status: int = None
    weekly_trade_frequency: str = None
    winRate: str = None


class SearchedTraderInfo(BaseModel):
    avatar: str = None
    be_trader: bool = None
    channel: str = None
    flag: str = None
    ip_country: str = None
    nation: str = None
    nick_name: str = None
    register_date: str = None
    register_ip_country: str = None
    short_uid: int = None
    team_id: int = None
    uid: int = None


class SearchedTraderAccountGradeVoInfo(BaseModel):
    api_identity: int = None
    label: int = None
    trader_grade: int = None
    uid: int = None


class SearchTraderInfoContainer(BaseModel):
    content: str = None
    has_new: bool = None
    labels: list = None  # unknown
    rank_stat: SearchTraderInfoRankStat = None  # unknown
    trader: SearchedTraderInfo = None  # unknown
    trader_account_grade_vo: SearchedTraderAccountGradeVoInfo = None  # unknown
    trader_public_recommend_status: Any = None  # unknown

    def get_nick_name(self) -> str:
        if self.trader:
            return self.trader.nick_name

        return

    def get_uid(self) -> int:
        if self.trader:
            return self.trader.uid

        return

    def get_api_identity(self) -> int:
        if self.trader_account_grade_vo:
            return self.trader_account_grade_vo.api_identity

        if self.rank_stat:
            return self.rank_stat.api_identity

        # TODO: later on add support for more cases
        return None

    def __str__(self):
        if not self.trader:
            return "No trader info"

        return f"uid: {self.trader.uid}; name: {self.trader.nick_name}; country: {self.trader.nation}"

    def __repr__(self):
        return self.__str__()


class SearchCopyTradersResult(BaseModel):
    expand_display: Any = None  # unknown
    fold_display: Any = None  # unknown
    page_id: int = None
    rank_desc: str = None
    rank_short_desc: str = None
    rank_statistic_days: int = None
    rank_tags: Any = None  # unknown
    rank_title: str = None
    rank_type: str = None
    result: list[SearchTraderInfoContainer] = None  # unknown
    search_result: bool = None
    total: int = None


class SearchCopyTradersResponse(BxApiResponse):
    data: SearchCopyTradersResult = None


# endregion

###########################################################

# region Account Assets types


class MinimalAssetInfo(BaseModel):
    asset_id: int = None
    asset_amount: Decimal = None
    asset_name: str = None
    has_value: bool = None


class TotalAssetsInfo(BaseModel):
    amount: Any = None  # unknown
    currency_amount: Decimal = None
    sign: str = None

    def __str__(self):
        return f"{dec_to_str(self.currency_amount)} {self.sign}"

    def __repr__(self):
        return self.__str__()


class AccountOverviewItem(BaseModel):
    account_name: str = None
    account_type: int = None
    total: TotalAssetsInfo = None  # unknown
    schema: str = None
    order: int = None

    def __str__(self):
        return f"{self.account_name} ({self.account_type}): {self.total}"


class AssetsInfoResult(BaseModel):
    total: TotalAssetsInfo = None
    account_overviews: list[AccountOverviewItem] = None
    recharge: int = None
    withdraw: int = None
    transfer: int = None
    exchange: int = None
    fault_flag: int = None
    fault_accounts: Any = None  # unknown


class AssetsInfoResponse(BxApiResponse):
    data: AssetsInfoResult = None


# endregion

###########################################################

# region Contracts types


class BasicCoinInfo(BaseModel):
    name: str = None

    def __str__(self):
        return f"{self.name} CoinInfo"

    def __repr__(self):
        return self.__str__()


class QuotationCoinVOInfo(BaseModel):
    id: int = None
    coin: BasicCoinInfo = None
    valuation_coin: BasicCoinInfo = None
    precision: int = None
    name: str = None
    market_status: int = None


class OrderDebitInfo(BaseModel):
    lend_coin: BasicCoinInfo = None
    amount: Decimal = None


class OrderOpenTradeInfo(BaseModel):
    traded_amount: Decimal = None
    traded_cash_amount: Decimal = None


class ContractOrderStatus(BaseModel):
    code: int = None
    value: str = None


class ContractTakeProfitInfo(BaseModel):
    id: int = None

    # this is id of the contract that this take-profit info belongs to.
    order_no: int = None
    margin_coin_name: str = None
    type: int = None
    margin: Decimal = None
    stop_rate: Decimal = None
    stop_price: Decimal = None
    close_style: int = None
    all_close: bool = None


class ContractStopLossInfo(BaseModel):
    id: int = None

    # this is id of the contract that this take-profit info belongs to.
    order_no: int = None
    margin_coin_name: str = None
    type: int = None
    margin: Decimal = None
    stop_rate: Decimal = None
    stop_price: Decimal = None
    close_style: int = None
    all_close: bool = None


class ProfitLossInfoContainer(BaseModel):
    loss_nums: int = None
    profit_nums: int = None
    profit_margin: Decimal = None
    loss_margin: Decimal = None
    profit_config: ContractTakeProfitInfo = None
    loss_config: ContractStopLossInfo = None


class ContractOrderInfo(BaseModel):
    order_no: int = None
    quotation_coin_vo: QuotationCoinVOInfo = None
    margin: Decimal = None
    margin_coin_name: str = None
    lever_times: Decimal = None
    display_lever_times: Decimal = None
    amount: Decimal = None  # margin * lever_times
    display_price: Decimal = None
    display_close_price: Decimal = None
    order_type: int = None
    close_type: int = None
    status: ContractOrderStatus = None
    open_date: str = None
    close_date: str = None
    fees: Decimal = None
    lever_fee: Decimal = None
    name: str = None
    order_create_type: int = None
    hide_price: bool = None
    fee_rate: Decimal = None
    hide: int = None
    liquidation_desc: str = None
    contract_account_mode: int = None
    current_price: Decimal = None
    sys_force_price: Decimal = None
    fund_type: int = None
    interest: Decimal = None
    order_open_trade: OrderOpenTradeInfo = None
    order_debit: OrderDebitInfo = None
    open_rate: Decimal = None
    close_rate: Decimal = None
    market_status: int = None
    create_time: str = None
    coupon_amount: Decimal = None
    stop_profit_modify_time: str = None
    stop_loss_modify_time: str = None
    show_adjust_margin: int = None
    trailing_stop: Decimal = None
    trailing_close_price: Decimal = None
    stop_rate: Decimal = None
    profit_loss_info: ProfitLossInfoContainer = None
    configs: Any = None  # just dictionaries of take-profit and stop-loss configs.
    stop_offset_rate: Decimal = None

    def is_long(self) -> bool:
        return self.order_type == 0

    def get_open_price(self) -> Decimal:
        return self.display_price

    def get_liquidation_price(self) -> Decimal:
        return self.sys_force_price

    def get_profit_str(self) -> str:
        last_price = self.current_price or self.display_close_price
        profit_or_loss = last_price - self.display_price
        profit_percentage = (profit_or_loss / self.display_price) * 100
        profit_percentage *= 1 if self.is_long() else -1
        return dec_to_str(profit_percentage * self.lever_times)

    def to_str(self, separator: str = "; ") -> str:
        result_str = f"{self.name} ({self.order_no}) "
        result_str += f"{ORDER_TYPES_MAP[self.order_type]} "
        result_str += f"{dec_to_str(self.lever_times)}x{separator}"
        result_str += f"margin: {dec_to_str(self.margin)} "
        result_str += f"{self.margin_coin_name}{separator}"

        if self.profit_loss_info:
            if self.profit_loss_info.profit_config:
                tp_config = self.profit_loss_info.profit_config
                result_str += f"TP: {dec_to_normalize(tp_config.stop_price)} "
                result_str += f"{tp_config.margin_coin_name}{separator}"
            if self.profit_loss_info.loss_config:
                sl_config = self.profit_loss_info.loss_config
                result_str += f"SL: {dec_to_normalize(sl_config.stop_price)}"
                result_str += f"{sl_config.margin_coin_name}{separator}"

        if self.sys_force_price:
            result_str += (
                f"liquidation: {dec_to_normalize(self.sys_force_price)}{separator}"
            )

        if self.current_price:
            result_str += (
                f"current price: {dec_to_normalize(self.current_price)}{separator}"
            )
        elif self.display_close_price:
            result_str += (
                f"close price: {dec_to_normalize(self.display_close_price)}{separator}"
            )
        profit_str = self.get_profit_str()
        result_str += f"profit: {profit_str}%"

        return result_str

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()


class ClosedContractOrderInfo(ContractOrderInfo):
    close_type_name: str = None
    gross_earnings: Decimal = None
    position_order: int = None


class MarginStatInfo(BaseModel):
    name: str = None
    margin_coin_name: str = None
    margin_type: int = None

    # total count of open contract orders in this margin-type.
    total: int = None


class ContractsListResult(BaseModel):
    orders: list[ContractOrderInfo] = None
    page_id: int = None
    margin_stats: list[MarginStatInfo] = None


class ContractsListResponse(BxApiResponse):
    data: ContractsListResult = None


class ContractOrdersHistoryResult(BaseModel):
    orders: list[ClosedContractOrderInfo] = None
    page_id: int = None


class ContractOrdersHistoryResponse(BxApiResponse):
    data: ContractOrdersHistoryResult = None

    def get_today_earnings(self, timezone: Any = pytz.UTC) -> Decimal:
        """
        Returns the total earnings for today.
        NOTE: This function will return None if there are no orders for today.
        """
        found_any_for_today: bool = False
        today_earnings = Decimal("0.00")
        today = datetime.now(timezone).date()
        if not self.data and self.msg:
            raise ExchangeError(self.msg)

        for current_order in self.data.orders:
            # check if the date is for today
            closed_date = (
                datetime.strptime(
                    current_order.close_date,
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )
                .astimezone(timezone)
                .date()
            )
            if closed_date == today:
                today_earnings += current_order.gross_earnings
                found_any_for_today = True

        if not found_any_for_today:
            return None

        return today_earnings

    def get_this_week_earnings(self, timezone: Any = pytz.UTC) -> Decimal:
        """
        Returns the total earnings for this week.
        NOTE: This function will return None if there are no orders for this week.
        """
        found_any_for_week: bool = False
        week_earnings = Decimal("0.00")
        today = datetime.now(timezone).date()
        week_start = today - timedelta(days=today.weekday())
        for current_order in self.data.orders:
            # check if the date is for this week
            closed_date = (
                datetime.strptime(
                    current_order.close_date,
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )
                .astimezone(timezone)
                .date()
            )
            if closed_date >= week_start:
                week_earnings += current_order.gross_earnings
                found_any_for_week = True

        if not found_any_for_week:
            return None

        return week_earnings

    def get_this_month_earnings(self, timezone: Any = pytz.UTC) -> Decimal:
        """
        Returns the total earnings for this month.
        NOTE: This function will return None if there are no orders for this month.
        """
        found_any_for_month: bool = False
        month_earnings = Decimal("0.00")
        today = datetime.now(timezone).date()
        month_start = today.replace(day=1)
        for current_order in self.data.orders:
            # check if the date is for this month
            closed_date = (
                datetime.strptime(
                    current_order.close_date,
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )
                .astimezone(timezone)
                .date()
            )
            if closed_date >= month_start:
                month_earnings += current_order.gross_earnings
                found_any_for_month = True

        if not found_any_for_month:
            return None

        return month_earnings

    def get_orders_len(self) -> int:
        if not self.data or not self.data.orders:
            return 0
        return len(self.data.orders)


class ContractConfigData(BaseModel):
    quotation_coin_id: int = None
    max_lever: OrderLeverInfo = None
    min_amount: Decimal = None
    levers: list[OrderLeverInfo] = None
    default_stop_loss_rate: Decimal = None
    default_stop_profit_rate: Decimal = None
    max_stop_loss_rate: Decimal = None
    max_stop_profit_rate: Decimal = None
    fee_rate: Decimal = None
    interest_rate: Decimal = None
    lever_fee_rate: Decimal = None
    sys_force_rate: Decimal = None
    new_sys_force_vo_list: list[SysForceVoInfo] = None
    margin_displays: list[MarginDisplayInfo] = None
    mlr: Decimal = None
    lsf: Decimal = None
    lsh: Decimal = None
    hold_amount: Decimal = None
    msr: Decimal = None
    sfa: Decimal = None
    available_asset: MinimalAssetInfo = None
    coupon_asset_value: Any = None
    contract_account_balance: MinimalAssetInfo = None
    delegate_order_up_threshold_rate: Any = None
    delegate_order_down_threshold_rate: Any = None
    profit_loss_extra_vo: Any = None
    fund_balance: Decimal = None
    balance: Decimal = None
    up_amount: Decimal = None
    down_amount: Decimal = None
    max_amount: Decimal = None
    stop_offset_rate: Decimal = None


class ContractConfigResponse(BxApiResponse):
    data: ContractConfigData = None


# endregion

###########################################################

# region contract delegation types


class CreateOrderDelegationData(BaseModel):
    order_id: str = None
    spread_rate: str = None


class CreateOrderDelegationResponse(BxApiResponse):
    data: CreateOrderDelegationData = None


# endregion

###########################################################

# region candle types


class SingleCandleInfo(MinimalCandleInfo):
    @staticmethod
    def deserialize_short(data: dict) -> "SingleCandleInfo":
        info = SingleCandleInfo()
        base: str = data.get("n", "")
        quote: str = data.get("m", "")
        info.pair = f"{base.upper()}/{quote.upper()}"
        info.open_price = as_decimal(data.get("o", None))
        info.close_price = as_decimal(data.get("c", None))
        info.volume = data.get("v", None)
        info.quote_volume = data.get("a", None)

        return info

    def __str__(self):
        return (
            f"{self.pair}, open: {self.open_price}, "
            f"close: {self.close_price}, volume: {self.quote_volume}"
        )
    
    def __repr__(self):
        return super().__str__()


# endregion

###########################################################
