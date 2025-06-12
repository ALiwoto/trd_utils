import pytest
# import asyncio

from trd_utils.exchanges import HyperLiquidClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_blofin_get_share_config():
    client = HyperLiquidClient()

    result = await client.get_trader_positions_info("0xefd3ab65915e35105caa462442c9ecc1346728df")

    assert result is not None

    print(f"total data length: {len(result.asset_positions)}")
    for current_info in result.asset_positions:
        print(f"  - current position: {current_info.position} ID: {current_info.get_position_id()}")