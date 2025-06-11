# from typing import Any, Optional
# from decimal import Decimal
# from datetime import datetime, timedelta
# import pytz

from decimal import Decimal
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

class CopyTraderInfoResponse(BlofinApiResponse):
    data: CopyTraderInfoResult = None
