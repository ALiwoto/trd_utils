import pytest

from trd_utils.exchanges import OkxClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_okx_get_copy_trader_positions():
    client = OkxClient()

    result = await client.get_trader_positions("2B6BDA00968EA9F8")

    assert result is not None
    assert result.data is not None

    for position in result.data[0].pos_data:
        print(f" - current position: {position}")

    await client.aclose()

@pytest.mark.asyncio
async def test_okx_get_copy_trader_info():
    client = OkxClient()

    result = await client.get_copy_trader_info("2B6BDA00968EA9F8")

    assert result is not None
    
    print(f"trader name: {result.pre_process.leader_account_info.nick_name}")

    await client.aclose()
