import pytest
# import asyncio

from trd_utils.exchanges import BlofinClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_blofin_get_share_config():
    client = BlofinClient()

    result = await client.get_share_config()

    assert result is not None
    assert result.code == 200
    assert result.data is not None

    print(f"total data length: {len(result.data.pnl_share_list)}")
    for current_info in result.data.pnl_share_list:
        print(f"  - current bg: {current_info.background_color}")

@pytest.mark.asyncio
async def test_blofin_get_cms_color():
    client = BlofinClient()

    result = await client.get_cms_color()

    assert result is not None
    assert result.code == 200
    assert result.data is not None

    print(f"country / color: {result.data.country} / {result.data.color}")

@pytest.mark.asyncio
async def test_blofin_get_copy_trader_info():
    client = BlofinClient()

    result = await client.get_copy_trader_info(
        uid=2897425892,
    )

    assert result is not None
    assert result.code == 200
    assert result.data is not None

    print(f"trader nickname: {result.data.nick_name}")

@pytest.mark.asyncio
async def test_blofin_get_copy_trader_order_list():
    client = BlofinClient()

    result = await client.get_copy_trader_order_list(
        from_param=0,
        limit_param=20,
        uid=2897425892,
    )

    assert result is not None
    assert result.code == 200
    assert result.data is not None

    print(f"Orders count: {len(result.data)}")

@pytest.mark.asyncio
async def test_blofin_get_copy_trader_order_history():
    client = BlofinClient()

    result = await client.get_copy_trader_order_history(
        from_param=0,
        limit_param=20,
        uid=2897425892,
    )

    assert result is not None
    assert result.code == 200
    assert result.data is not None

    print(f"Orders count: {len(result.data)}")

