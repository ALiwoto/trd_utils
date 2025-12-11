import asyncio

import pytest

# import asyncio
from trd_utils.exchanges import BinanceClient
from trd_utils.types_helper import base_model

LOCAL_PROXY_URL = "http://localhost:4141"

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True


class FilterContainer:
    my_pairs: list = []
    quote_currency: str = "USDT"

    def __init__(self, quote_currency: str):
        self.quote_currency = quote_currency

        for base in [
            "BTC",
            "ETH",
            "XRP",
            "LTC",
            "ADA",
            "SOL",
            "DOT",
            "DOGE",
            "AVAX",
            "MATIC",
        ]:
            pair = f"{base}/{quote_currency}:{quote_currency}"
            self.my_pairs.append(pair)

    async def my_filter_func(self, pair: str, **kwargs) -> bool:
        await asyncio.sleep(0)  # to make it async
        if ":" not in pair:
            pair += ":" + self.quote_currency
        return pair in self.my_pairs


@pytest.mark.asyncio
async def test_binance_get_futures_market_info():
    async with BinanceClient() as client:
        client.set_proxy_base_url(LOCAL_PROXY_URL)
        if await client.is_proxy_available():
            print(f"using proxy url: {LOCAL_PROXY_URL}")
        else:
            client.set_proxy_base_url(None)
        await do_market_info_by_quote(client, FilterContainer("USDT"))
        await do_market_info_by_quote(client, FilterContainer("USDC"))


async def do_market_info_by_quote(client: BinanceClient, filter_obj: FilterContainer):
    result = await client.get_unified_futures_market_info(
        sort_by="percentage_change_24h",
        descending=True,
        filter_quote_token=filter_obj.quote_currency,
        filter_func=filter_obj.my_filter_func,
    )

    assert result is not None

    print(f"total {filter_obj.quote_currency} markets: {len(result.sorted_markets)}")
    for current_market in result.sorted_markets:
        print(current_market)
