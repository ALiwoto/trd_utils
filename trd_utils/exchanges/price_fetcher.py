

from datetime import datetime
from decimal import Decimal

import pytz
from trd_utils.types_helper import BaseModel


class MinimalCandleInfo(BaseModel):
    # The pair in format of BTC/USDT.
    pair: str = None

    # This candle's open price.
    open_price: Decimal = None

    # The close price.
    close_price: Decimal = None

    # volume in the first pair (e.g. BTC).
    volume: Decimal = None

    # volume in the second part of the pair (e.g. USDT).
    quote_volume: Decimal = None

    # The time this candle info was retrieved.
    fetched_at: datetime = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fetched_at = datetime.now(tz=pytz.UTC)


class IPriceFetcher:
    """
    The IPriceFetcher class acts as an interface for classes that support
    fetching last candle of a specific pair, without any specific floodwait or
    ratelimit applied on the method itself (because e.g. they are fetching it
    through a background websocket connection).
    Please do not use this class directly, instead use a class that inherits
    and implements the methods of this class (e.g. one of the exchange classes).
    """

    async def do_price_subscribe(self) -> None:
        pass

    async def get_last_candle(self, pair: str) -> MinimalCandleInfo:
        pass
