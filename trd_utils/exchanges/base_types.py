

from datetime import datetime
from decimal import Decimal

class UnifiedPositionInfo:
    # The id of the position.
    position_id: str = None

    # The pnl (profit) of the position.
    position_pnl: Decimal = None

    # The position side, either "LONG" or "SHORT".
    position_side: str = None

    # The formatted pair string of this position.
    # e.g. BTC/USDT.
    position_pair: str = None

    # Side but with a proper emoji alongside of it.
    side_with_emoji: str = None

    # The open time of this position.
    # Note that not all public APIs might provide this field.
    open_time: datetime = None

    # The relative open time of this position.
    relative_open_time: str = None

    # Open price of the position.
    open_price: Decimal = None

    # The string (and formatted) version of the open_price.
    # Optionally base unit also included (e.g. USDT or USD).
    open_price_str: str = None


class UnifiedTraderPositions:
    positions: list[UnifiedPositionInfo] = None

class UnifiedTraderInfo:
    # Name of the trader
    trader_name: str = None

    # The URL in which we can see the trader's profile
    trader_url: str = None

    # Trader's id. Either int or str. In DEXes (such as HyperLiquid),
    # this might be wallet address of the trader.
    trader_id: int | str = None

    # Trader's win-rate. Not all exchanges might support this field.
    win_rate: Decimal = None
