from datetime import datetime
from decimal import Decimal

from trd_utils.types_helper.base_model import BaseModel


class UnifiedPositionInfo(BaseModel):
    # The id of the position.
    position_id: str = None

    # The pnl (profit) of the position.
    position_pnl: Decimal = None

    # The position side, either "LONG" or "SHORT".
    position_side: str = None

    # The position's leverage.
    position_leverage: Decimal = None

    # The margin mode; e.g. cross or isolated. Please note that
    # different exchanges might provide different kinds of margin modes,
    # depending on what they support, that's why we can't support a unified
    # enum type for this as of yet.
    margin_mode: str = None

    # The formatted pair string of this position.
    # e.g. BTC/USDT.
    position_pair: str = None

    # The open time of this position.
    # Note that not all public APIs might provide this field.
    open_time: datetime = None

    # Open price of the position.
    open_price: Decimal = None

    # The base unit that the open-price is based on (e.g. USD, USDT, USDC)
    open_price_unit: str | None = None

    # The last price of this pair on the target exchange.
    # not all exchanges support this yet, so use it with caution.
    last_price: Decimal | None = None

    # The last volume of this pair being traded on the target exchange.
    # not all exchanges support this yet, so use it with caution.
    last_volume: Decimal | None = None

    def __str__(self):
        parts = []

        # Add position pair and ID
        parts.append(
            f"Position: {self.position_pair or 'Unknown'} (ID: {self.position_id or 'N/A'})"
        )

        # Add side and leverage
        side_str = f"Side: {self.position_side or 'Unknown'}"
        if self.position_leverage is not None:
            side_str += f", {self.position_leverage}x"
        parts.append(side_str)

        # Add margin mode if available
        if self.margin_mode:
            parts.append(f"Margin: {self.margin_mode}")

        # Add open price if available
        price_str = "Open price: "
        if self.open_price is not None:
            price_str += f"{self.open_price}"
            if self.open_price_unit:
                price_str += f" {self.open_price_unit}"
        else:
            price_str += "N/A"
        parts.append(price_str)

        # Add open time if available
        if self.open_time:
            parts.append(f"Opened: {self.open_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Add PNL if available
        if self.position_pnl is not None:
            parts.append(f"PNL: {self.position_pnl}")

        return " | ".join(parts)

    def __repr__(self):
        return self.__str__()


class UnifiedTraderPositions(BaseModel):
    positions: list[UnifiedPositionInfo] = None


class UnifiedTraderInfo(BaseModel):
    # Trader's id. Either int or str. In DEXes (such as HyperLiquid),
    # this might be wallet address of the trader.
    trader_id: int | str = None

    # Name of the trader
    trader_name: str = None

    # The URL in which we can see the trader's profile
    trader_url: str = None

    # Trader's win-rate. Not all exchanges might support this field.
    win_rate: Decimal = None

    def get_win_rate_str(self) -> str:
        return str(round(self.win_rate, 2)) if self.win_rate is not None else "N/A"

    def __str__(self):
        return (
            f"{self.trader_name} ({self.trader_id})"
            f" | Win Rate: {self.get_win_rate_str()}"
            f" | Profile: {self.trader_url}"
        )

    def __repr__(self):
        return self.__str__()
