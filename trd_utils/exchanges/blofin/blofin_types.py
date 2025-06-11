# from typing import Any, Optional
# from decimal import Decimal
# from datetime import datetime, timedelta
# import pytz

from decimal import Decimal
from typing import Any
from trd_utils.types_helper import BaseModel

# from trd_utils.common_utils.float_utils import (
#     dec_to_str,
#     dec_to_normalize,
# )



class BlofinApiResponse(BaseModel):
    code: int = None
    timestamp: int = None
    msg: str = None

    def __str__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"

    def __repr__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"


###########################################################

class PnlShareListInfo(BaseModel):
    background_color: str = None
    background_img_up: str = None
    background_img_down: str = None

class ShareConfigResult(BaseModel):
    pnl_share_list: list[PnlShareListInfo] = None

class ShareConfigResponse(BlofinApiResponse):
    data: ShareConfigResult = None

class CmsColorResult(BaseModel):
    color: str = None
    city: str = None
    country: str = None
    ip: str = None

class CmsColorResponse(BlofinApiResponse):
    data: CmsColorResult = None

###########################################################


class CopyTraderInfoResult(BaseModel):
    aum: str = None
    can_copy: bool = None
    copier_whitelist: bool = None
    follow_state: int = None
    followers: int = None
    followers_max: int = None
    forbidden_follow_type: int = None
    hidden_all: bool = None
    hidden_order: bool = None
    joined_date: int = None
    max_draw_down: Decimal = None
    nick_name: str = None
    order_amount_limit: None
    profile: str = None
    profit_sharing_ratio: Decimal = None
    real_pnl: Decimal = None
    roi_d7: Decimal = None
    self_introduction: str = None
    sharing_period: str = None
    source: int = None
    uid: int = None
    whitelist_copier: bool = None
    win_rate: Decimal = None

    def get_profile_url(self) -> str:
        return f"https://blofin.com/copy-trade/details/{self.uid}"

class CopyTraderInfoResponse(BlofinApiResponse):
    data: CopyTraderInfoResult = None

class CopyTraderSingleOrderInfo(BaseModel):
    id: int = None
    symbol: str = None
    leverage: int = None
    order_side: str = None
    avg_open_price: str = None
    quantity: str = None
    quantity_cont: None
    open_time: int = None
    close_time: Any = None
    avg_close_price: Decimal = None
    real_pnl: Any = None
    close_type: Any = None
    roe: Decimal = None
    followers_profit: Decimal = None
    followers: Any = None
    order_id: Any = None
    sharing: Any = None
    order_state: None
    trader_name: None
    mark_price: None
    tp_trigger_price: None
    tp_order_type: None
    sl_trigger_price: None
    sl_order_type: None
    margin_mode: str = None
    time_in_force: None
    position_side: str = None
    order_category: None
    price: None
    fill_quantity: None
    fill_quantity_cont: None
    pnl: None
    cancel_source: None
    order_type: None
    order_open_state: None
    amount: None
    filled_amount: None
    create_time: None
    update_time: None
    open_fee: None
    close_fee: None
    id_md5: None
    tp_sl: None
    trader_uid: None
    available_quantity: None
    available_quantity_cont: None
    show_in_kline: None
    unrealized_pnl: None
    unrealized_pnl_ratio: None
    broker_id: None
    position_change_history: None
    user_id: None

class CopyTraderOrderListResponse(BlofinApiResponse):
    data: list[CopyTraderSingleOrderInfo] = None

class CopyTraderAllOrderList(CopyTraderOrderListResponse):
    total_count: int = None

class CopyTraderOrderHistoryResponse(BlofinApiResponse):
    data: list[CopyTraderSingleOrderInfo] = None

class CopyTraderAllOrderHistory(CopyTraderOrderHistoryResponse):
    total_count: int = None
