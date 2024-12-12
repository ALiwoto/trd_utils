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

    print(result)

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_user_favorite_quotation():
    client = BXUltraClient()

    result = await client.get_user_favorite_quotation()

    assert result is not None
    assert result["code"] == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_bx_get_quotation_rank():
    client = BXUltraClient()

    result = await client.get_quotation_rank()

    assert result is not None
    assert result["code"] == 0

    await client.aclose()


@pytest.mark.asyncio
async def test_bx_hot_search():
    client = BXUltraClient()

    result = await client.get_hot_search()

    assert result is not None
    assert result["code"] == 0

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
    assert result["code"] == 0

    await client.aclose()








