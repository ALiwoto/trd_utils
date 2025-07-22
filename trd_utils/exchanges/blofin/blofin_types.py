from decimal import Decimal
from typing import Any
from trd_utils.types_helper import BaseModel


###########################################################

# region common types


class BlofinApiResponse(BaseModel):
    code: int = None
    timestamp: int = None
    msg: str = None

    def __str__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"

    def __repr__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}"


# endregion

###########################################################

# region api-config types


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


# endregion

###########################################################

# region copy-trader types


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
    order_amount_limit: Any = None
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
    avg_open_price: Decimal = None
    quantity: Decimal = None
    quantity_cont: Any = None
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
    order_state: Any = None
    trader_name: Any = None
    mark_price: Any = None
    tp_trigger_price: Any = None
    tp_order_type: Any = None
    sl_trigger_price: Any = None
    sl_order_type: Any = None
    margin_mode: str = None
    time_in_force: Any = None
    position_side: str = None
    order_category: Any = None
    price: Any = None
    fill_quantity: Any = None
    fill_quantity_cont: Any = None
    pnl: Decimal = None
    cancel_source: Any = None
    order_type: Any = None
    order_open_state: Any = None
    amount: Any = None
    filled_amount: Any = None
    create_time: Any = None
    update_time: Any = None
    open_fee: Any = None
    close_fee: Any = None
    id_md5: Any = None
    tp_sl: Any = None
    trader_uid: Any = None
    available_quantity: Any = None
    available_quantity_cont: Any = None
    show_in_kline: Any = None
    unrealized_pnl: Any = None
    unrealized_pnl_ratio: Any = None
    broker_id: Any = None
    position_change_history: Any = None
    user_id: Any = None

    def get_initial_margin(self) -> Decimal:
        if not self.avg_open_price or not self.quantity or not self.leverage:
            return None
        return (self.avg_open_price * self.quantity) / self.leverage


class CopyTraderOrderListResponse(BlofinApiResponse):
    data: list[CopyTraderSingleOrderInfo] = None


class CopyTraderAllOrderList(CopyTraderOrderListResponse):
    total_count: int = None


class CopyTraderOrderHistoryResponse(BlofinApiResponse):
    data: list[CopyTraderSingleOrderInfo] = None


class CopyTraderAllOrderHistory(CopyTraderOrderHistoryResponse):
    total_count: int = None


# endregion

###########################################################
