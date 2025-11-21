import pytest
# import asyncio

from trd_utils.exchanges import BinanceClient


@pytest.mark.asyncio
async def test_blofin_get_futures_market_info():
    async with BinanceClient() as client:
        result = await client.get_unified_futures_market_info(
            sort_by="percentage_change_24h",
            descending=True,
        )

        assert result is not None

        print(f"total markets: {len(result.sorted_markets)}")
        for current_market in result.sorted_markets:
            print(current_market)
