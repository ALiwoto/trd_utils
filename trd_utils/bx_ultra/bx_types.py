from typing import Any
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
    name: str
    coin_type: int
    valuation_coin_name: str
    coin_name: str
    icon_name: str
    slug: str
    quotation_id: int
    open: Decimal
    close: Decimal
    weight: int
    favorite_flag: Any # unknown
    precision: int
    coin_precision: int
    valuation_precision: int
    market_status: Any # unknown
    trader_scale: Decimal
    coin_id: int
    valuation_coin_id: int
    status: Any # unknown
    open_time: Any # unknown
    open_price: Any # unknown
    high24: Decimal
    low24: Decimal
    volume24: Decimal
    amount24: Decimal
    market_val: Decimal
    full_name: str
    biz_type: int

    def __str__(self):
        return f"{self.coin_name}/{self.valuation_coin_name}; price: {self.close}; vol: {self.market_val}"
    
    def __repr__(self):
        return f"{self.coin_name}/{self.valuation_coin_name}; price: {self.close}; vol: {self.market_val}"

class ZoneModuleInfo(BaseModel):
    id: int
    name: str
    quotation_list: list[CoinQuotationInfo]
    zone_name: str
    weight: int
    biz_type: int

    def __str__(self):
        return f"{self.name} ({self.zone_name})"
    
    def __repr__(self):
        return f"{self.name} ({self.zone_name})"

class ZoneModuleListResult(BaseModel):
    zone_module_list: list[ZoneModuleInfo]
    biz_type: int
    need_channel_type: list[int]
    icon_url_prefix: str


class ZoneModuleListResponse(BxApiResponse):
    data: ZoneModuleListResult

