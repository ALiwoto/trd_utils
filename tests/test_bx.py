import pytest

from trd_utils.bx_ultra.bx_ultra_client import BXUltraClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_bx_get_zone_module_info():
    client = BXUltraClient()

    result = await client.get_zone_module_info()

    assert result is not None
    assert result.code == 0

    print("available zones are: " + ", ".join(result.data.zone_module_list.name))

    for current_zone in result.data.zone_module_list:
        print(f"Zone: {current_zone.zone_name}")
        for current_quotation in current_zone.quotation_list:
            print(f" - {current_quotation}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_user_favorite_quotation():
    client = BXUltraClient()

    result = await client.get_user_favorite_quotation()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    if result.data.swap_list:
        print("swaps:")
        for current_swap in result.data.swap_list:
            print(f" - {current_swap}")

    if result.data.coin_margin_list:
        print("coin margins:")
        for current_coin_margin in result.data.coin_margin_list:
            print(f" - {current_coin_margin}")
    
    if result.data.usdt_margin_list:
        print("usdt margins:")
        for current_usdt_margin in result.data.usdt_margin_list:
            print(f" - {current_usdt_margin}")

    await client.aclose()


@pytest.mark.asyncio
async def test_bx_get_quotation_rank():
    client = BXUltraClient()

    result = await client.get_quotation_rank()

    assert result is not None
    assert result.code == 0

    for current_rank in result.data.rank_list:
        for current_biz in current_rank.rank_biz_list:
            print(f"{current_rank.rank_name} / {current_biz.biz_name}:")
            for current_quotation in current_biz.quotation_list:
                print(f" - {current_quotation}")

    await client.aclose()


@pytest.mark.asyncio
async def test_bx_hot_search():
    client = BXUltraClient()

    result = await client.get_hot_search()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("hot searches:")
    for current_search in result.data.result:
        print(f"{current_search.coin_name} ({current_search.symbol})")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_assets_info():
    client = BXUltraClient()

    result = await client.get_assets_info()

    assert result is not None
    assert result["code"] == 0

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_homepage():
    client = BXUltraClient()

    result = await client.get_homepage()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    await client.aclose()






