import pytest

from trd_utils.exchanges import OkxClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_okx_get_copy_trader_positions1():
    client = OkxClient()

    result = await client.get_trader_positions("2B6BDA00968EA9F8")

    assert result is not None
    assert result.data is not None

    for position in result.data[0].pos_data:
        print(f" - current position: {position}")
    
    # make sure everything is serializable
    _ = type(result).deserialize(result.serialize())

    await client.aclose()

@pytest.mark.asyncio
async def test_okx_get_copy_trader_positions2():
    client = OkxClient()

    result = await client.get_trader_positions("BF1FD9E90D802348")

    assert result is not None
    assert result.data is not None

    for position in result.data[0].pos_data:
        print(f" - current position: {position}")
    
    # make sure everything is serializable
    _ = type(result).deserialize(result.serialize())

    await client.aclose()

@pytest.mark.asyncio
async def test_okx_get_copy_trader_info1():
    client = OkxClient()

    result = await client.get_copy_trader_info("2B6BDA00968EA9F8")

    assert result is not None
    
    print(f"trader name: {result.pre_process.leader_account_info.nick_name}")

    await client.aclose()

@pytest.mark.asyncio
async def test_okx_get_copy_trader_info2():
    client = OkxClient()

    result = await client.get_copy_trader_info("BF1FD9E90D802348")

    assert result is not None

    # make sure everything is serializable
    _ = type(result).deserialize(result.serialize())
    
    print(f"trader name: {result.pre_process.leader_account_info.nick_name}")

    await client.aclose()
