
from decimal import Decimal
from trd_utils.types_helper import BaseModel


###########################################################
# region Leaderboard Types (B-API)


class BinanceLeaderboardPosition(BaseModel):
    symbol: str = None
    entry_price: Decimal = None
    mark_price: Decimal = None
    pnl: Decimal = None
    roe: Decimal = None
    amount: Decimal = None
    leverage: int = None
    update_time_stamp: int = None
    
    # Binance sometimes returns this to indicate side, though amount sign is also used.
    # It might be a list or a boolean depending on specific endpoint versions, 
    # but for "getOtherPosition" it is often implied. 
    # We will define it just in case the API maps it.
    long_short: bool | list = None

    def get_side(self) -> str:
        """
        Determines the side (LONG/SHORT) of the position.
        """
        # Strategy 1: Check specific long_short field if populated
        if isinstance(self.long_short, bool):
            return "LONG" if self.long_short else "SHORT"
        
        if isinstance(self.long_short, list) and len(self.long_short) > 0:
            # sometimes ["LONG"] or ["SHORT"]
            val = str(self.long_short[0]).upper()
            if "LONG" in val:
                return "LONG"
            if "SHORT" in val:
                return "SHORT"

        # Strategy 2: Check amount sign (standard for most derivatives APIs)
        if self.amount is not None:
            if self.amount > 0:
                return "LONG"
            elif self.amount < 0:
                return "SHORT"

        return "UNKNOWN_SIDE"

    def get_position_id(self, uid: str) -> str:
        """
        Generates a synthetic position ID.
        Binance Leaderboard does not provide a persistent ID for the position.
        """
        side_str = self.get_side()
        side_code = 1 if side_str == "LONG" else 0
        
        # ID = {UID}-{SYMBOL}-{SIDE_CODE}
        raw_str = f"{uid}-{self.symbol}-{side_code}"
        return raw_str.encode("utf-8").hex()


class BinanceLeaderboardResponseData(BaseModel):
    other_position_ret_list: list[BinanceLeaderboardPosition] = None
    update_time_stamp: int = None


class BinanceLeaderboardResponse(BaseModel):
    code: str = None
    message: str = None
    message_detail: str = None
    data: BinanceLeaderboardResponseData = None
    success: bool = False


class BinanceLeaderboardBaseInfo(BaseModel):
    nick_name: str = None
    user_photo_url: str = None
    introduction: str = None


class BinanceLeaderboardBaseInfoResponse(BaseModel):
    data: BinanceLeaderboardBaseInfo = None
    success: bool = False
    code: str = None


# endregion

###########################################################
# region Market Data Types (F-API)


class BinanceTicker24h(BaseModel):
    symbol: str = None
    last_price: Decimal = None
    prev_close_price: Decimal | None = None
    price_change: Decimal = None
    price_change_percent: Decimal = None
    weighted_avg_price: Decimal = None
    # quote_volume is the volume in USDT (Turnover)
    quote_volume: Decimal = None
    # volume is the volume in Base Asset (e.g. BTC)
    volume: Decimal = None 


class BinancePremiumIndex(BaseModel):
    symbol: str = None
    last_funding_rate: Decimal = None
    mark_price: Decimal = None
    index_price: Decimal = None
    time: int = None


# endregion
