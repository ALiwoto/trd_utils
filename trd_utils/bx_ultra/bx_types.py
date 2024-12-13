from typing import Any, Optional
from ..types_helper import BaseModel
from decimal import Decimal

class BxApiResponse(BaseModel):
    code: int
    timestamp: int

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
    favorite_flag: Any = None # unknown
    precision: int = None
    coin_precision: int = None
    valuation_precision: int = None
    market_status: Any = None # unknown
    trader_scale: Decimal = None
    coin_id: int = None
    valuation_coin_id: int = None
    status: Any = None # unknown
    open_time: Any = None # unknown
    open_price: Any = None # unknown
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

###########################################################

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

###########################################################

class UserFavoriteQuotationResult(BaseModel):
    usdt_margin_list: list[CoinQuotationInfo] = None
    coin_margin_list: list[CoinQuotationInfo] = None
    swap_list: list[CoinQuotationInfo] = None
    biz_type: int = None
    icon_url_prefix: str = None
    recommend: bool = None

class UserFavoriteQuotationResponse(BxApiResponse):
    data: UserFavoriteQuotationResult = None

###########################################################

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

###########################################################

class HotSearchItem(BaseModel):
    symbol: str = None
    coin_name: str = None
    val_coin_name: str = None
    weight: int = None


class HotSearchResult(BaseModel):
    result: list[HotSearchItem] = None
    hint_ab_test: bool = None
    page_id: int = None
    total: int = None

class HotSearchResponse(BxApiResponse):
    data: HotSearchResult = None

###########################################################

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
        self,
        j_data: dict,
        module_name: str,
        module_type: int
    ) -> bool:
        return self.module_name == module_name or \
            j_data.get("moduleName", None) == module_name or \
            self.module_type == module_type or \
            j_data.get("moduleType", None) == module_type

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
        return (f"{self.module_name} ({self.module_type}): {self.module_desc};" +
            f" {len(self.item_list)} items")
    
    def __repr__(self):
        return (f"{self.module_name} ({self.module_type}): {self.module_desc};" +
            f" {len(self.item_list)} items")

class HomePageResult(BaseModel):
    icon_prefix: str = None
    green_amount_img_prefix: str = None
    red_amount_img_prefix: str = None
    module_list: list[HomePageModuleInfo] = None

class HomePageResponse(BxApiResponse):
    data: HomePageResult = None

