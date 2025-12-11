import pytest
# import asyncio

from trd_utils.exchanges import HyperLiquidClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

LOCAL_PROXY_URL = "http://localhost:4141"


@pytest.mark.asyncio
async def test_hl_get_position_info():
    async with HyperLiquidClient() as client:
        result = await client.get_trader_positions_info(
            "0xefd3ab65915e35105caa462442c9ecc1346728df"
        )

        assert result is not None

        print(f"total data length: {len(result.asset_positions)}")
        for current_info in result.asset_positions:
            print(
                f"  - current position: {current_info.position} ID: {current_info.get_position_id()}"
            )


@pytest.mark.asyncio
async def test_hl_get_futures_market_info():
    async with HyperLiquidClient() as client:
        client.set_proxy_base_url(LOCAL_PROXY_URL)
        if await client.is_proxy_available():
            print(f"using proxy url: {LOCAL_PROXY_URL}")
        else:
            client.set_proxy_base_url(None)

        result = await client.get_unified_futures_market_info(
            sort_by="percentage_change_24h",
            descending=True,
        )

        assert result is not None

        print(f"total markets: {len(result.sorted_markets)}")
        for current_market in result.sorted_markets:
            print(current_market)

        market = result.find_market_by_name("kPEPE")
        assert market is not None
        print(f"found market by name 'kPEPE': {market}")
