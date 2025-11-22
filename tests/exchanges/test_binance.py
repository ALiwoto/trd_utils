import pytest
# import asyncio

from trd_utils.exchanges import BinanceClient
from trd_utils.types_helper import base_model


# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_binance_get_futures_market_info():
    async with BinanceClient() as client:
        await do_market_info_by_quote(client, "USDT")
        await do_market_info_by_quote(client, "USDC")
    
async def do_market_info_by_quote(client: BinanceClient, quote_token: str):
    result = await client.get_unified_futures_market_info(
        sort_by="percentage_change_24h",
        descending=True,
        filter_quote_token=quote_token,
    )

    assert result is not None

    print(f"total {quote_token} markets: {len(result.sorted_markets)}")
    for current_market in result.sorted_markets:
        print(current_market)
