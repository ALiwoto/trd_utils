from datetime import datetime
from decimal import Decimal
from html.parser import HTMLParser
from typing import Any
from trd_utils.types_helper import BaseModel


###########################################################

# region common types


class OkxApiResponse(BaseModel):
    code: int = None
    msg: str = None

    def __str__(self):
        return f"code: {self.code}; timestamp: {self.timestamp}; {getattr(self, 'data', None)}"

    def __repr__(self):
        return self.__str__()


# endregion

###########################################################

# region user-positions types


class UserPositionInfo(BaseModel):
    alias: str = None
    avg_px: Decimal = None
    be_px: Decimal = None
    c_time: datetime = None
    fee: Decimal = None
    funding_fee: Decimal = None
    inst_id: str = None
    inst_type: str = None
    last: Decimal = None
    lever: Decimal = None
    liq_px: Decimal = None
    margin: Decimal = None
    mark_px: Decimal = None
    mgn_mode: str = None
    mgn_ratio: Decimal = None
    notional_usd: Decimal = None
    pnl: Decimal = None
    pos: Decimal = None
    pos_ccy: str = None
    pos_id: str = None
    pos_side: str = None  # not that position side
    quote_ccy: str = None
    realized_pnl: Decimal = None
    upl: Decimal = None
    upl_ratio: Decimal = None

    def get_side(self) -> str:
        if self.pos > 0:
            return "LONG"
        return "SHORT"
    
    def get_pair(self) -> str:
        my_inst = self.inst_id.split("-")
        if len(my_inst) > 1:
            if my_inst[1] == "USD":
                my_inst[1] = "USDT"

            return f"{my_inst[0]}/{my_inst[1]}"
        # fallback to USDT
        return f"{self.pos_ccy}/USDT"
        


class CurrentUserPositionsResult(BaseModel):
    long_lever: Decimal = None
    short_lever: Decimal = None
    pos_data: list[UserPositionInfo] = None


class CurrentUserPositionsResponse(OkxApiResponse):
    data: list[CurrentUserPositionsResult] = None


# endregion

###########################################################

# region User Info types


class UserOverviewData(BaseModel):
    ccy: str = None
    equity: Decimal = None
    max_retreat: Decimal = None
    onboard_duration: int = None
    pnl: Decimal = None
    pnl_ratio: Decimal = None
    risk_reward_ratio: str = None
    win_rate: Decimal = None
    withdrawal: Decimal = None


class AuthInfo(BaseModel):
    is_new_user: bool = None
    user_guidance: bool = None
    is_show_smart_copy: bool = None
    is_cr_market_white_list_user: bool = None
    is_show_min_entry_mount: bool = None
    is_show_trader_tier: bool = None
    auth_info_has_loaded: bool = None


class LeaderAccountInfo(BaseModel):
    unique_name: str = None
    api_trader: int = None
    portrait: str = None
    nick_name: str = None
    en_nick_name: str = None
    sign: str = None
    translated_bio: str = None
    en_sign: str = None
    day: int = None
    count: str = None
    followee_num: int = None
    target_id: str = None
    role_type: int = None
    spot_role_type: int = None
    public_status: int = None
    country_id: str = None
    is_strategy_lead: bool = None
    is_signal_trader: bool = None
    country_name: str = None
    show_country_tag: bool = None
    is_chinese: bool = None
    is_followed: bool = None
    tier: Any = None


class PreProcessUerInfo(BaseModel):
    leader_account_info: LeaderAccountInfo = None
    auth_info: AuthInfo = None


class UserInfoInitialProps(BaseModel):
    overview_data: UserOverviewData = None
    pre_process: PreProcessUerInfo = None


class AppContextUserInfo(BaseModel):
    """
    The class which holds an AppContext related to a certain user's info
    on the exchange.
    """

    initial_props: UserInfoInitialProps = None
    is_ssr: bool = None
    faas_use_ssr: bool = None
    use_ssr: bool = None
    is_ssr_success: bool = None
    dsn: str = None
    template_config: None = None
    version: str = None
    project: str = None
    url_key: str = None
    trace_id: str = None
    enable_rtl: bool = None
    is_apm_proxy_off: int = None
    is_yandex_off: int = None
    is_web_worker_enable: int = None


class UserInfoHtmlParser(HTMLParser):
    target_data_id: str = None
    found_value: str = None
    current_tag_has_target: bool = None

    def __init__(self, target_data_id: str, **kwargs):
        super().__init__(**kwargs)
        self.target_data_id = target_data_id
        self.found_value = None
        self.current_tag_has_target = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)
        if "data-id" in attrs_dict and attrs_dict["data-id"] == self.target_data_id:
            self.current_tag_has_target = True

    def handle_data(self, data: str):
        if self.current_tag_has_target:
            self.found_value = data
            self.current_tag_has_target = False


# endregion

###########################################################
