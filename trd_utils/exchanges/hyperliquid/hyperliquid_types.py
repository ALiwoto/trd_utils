from decimal import Decimal
from trd_utils.types_helper import BaseModel


###########################################################


# region Common types


class HyperLiquidApiResponse(BaseModel):
    time: int = None


# endregion

###########################################################


# region info types


class CumFundingInfo(BaseModel):
    all_time: str = None
    since_open: str = None
    since_change: str = None


class LeverageInfo(BaseModel):
    type: str = None
    value: int = None


class PositionInfo(BaseModel):
    coin: str = None
    szi: Decimal = None
    leverage: LeverageInfo = None
    entry_px: Decimal = None
    position_value: Decimal = None
    unrealized_pnl: Decimal = None
    return_on_equity: Decimal = None
    liquidation_px: Decimal = None
    margin_used: Decimal = None
    max_leverage: int = None
    cum_funding: CumFundingInfo = None

    def get_side(self) -> str:
        if self.szi > 0:
            return "LONG"
        elif self.szi < 0:
            return "SHORT"
        return "UNKNOWN_SIDE"

    def get_position_id(self) -> str:
        """
        As far as I know, the API endpoint does not return the position id,
        maybe it only returns it to the account owner?
        In any case, we will have to somehow fake it in order to be able to compare
        it with other positions...
        """
        return (
            f"{self.coin}-{self.leverage.value}-{1 if self.szi > 0 else 0}"
        ).encode("utf-8").hex()

    def get_leverage(self) -> str:
        return f"{self.leverage.value}x ({self.leverage.type})"

    def __repr__(self):
        return (
            f"{self.get_side()} {self.get_leverage()} {self.coin} "
            f"Margin: {self.margin_used}, PNL: {self.unrealized_pnl}"
        )

    def __str__(self):
        return self.__repr__()


class AssetPosition(BaseModel):
    type: str = None
    position: PositionInfo = None

    def __repr__(self):
        return f"{self.position}; {self.type}"

    def __str__(self):
        return self.__str__()
    
    def get_position_id(self) -> str:
        return self.position.get_position_id()


class MarginSummaryInfo(BaseModel):
    account_value: Decimal = None
    total_ntl_pos: Decimal = None
    total_raw_usd: Decimal = None
    total_margin_used: Decimal = None


class TraderPositionsInfoResponse(BaseModel):
    margin_summary: MarginSummaryInfo = None
    cross_margin_summary: MarginSummaryInfo = None
    cross_maintenance_margin_used: Decimal = None
    withdrawable: Decimal = None
    asset_positions: list[AssetPosition] = None


# endregion

###########################################################
