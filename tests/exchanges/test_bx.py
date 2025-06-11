import pytest
import asyncio

from trd_utils.exchanges import BXUltraClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_bx_get_earning_amounts():
    client = BXUltraClient()

    today_earnings = await client.get_today_contract_earnings()
    print(f"Today's earnings: {today_earnings}")

    this_week_earnings = await client.get_this_week_contract_earnings()
    print(f"This week's earnings: {this_week_earnings}")

    this_month_earnings = await client.get_this_month_contract_earnings()
    print(f"This month's earnings: {this_month_earnings}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_contract_order_history():
    client = BXUltraClient()

    result = await client.get_contract_order_history(
        page_id=0,
        paging_size=10,
        margin_coin_name="USDT",
    )

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("Order History: ")
    for current_order in result.data.orders:
        print(f" - {current_order}")
    
    today_earning = result.get_today_earnings()
    print(f"Today's earnings: {today_earning}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_contract_lists():
    client = BXUltraClient()

    result = await client.get_contract_list(page_id=0, page_size=1)
    per_page_size = 10

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("Margin Status: ")
    for current_stat in result.data.margin_stats:
        print(f" - {current_stat.margin_coin_name}: {current_stat.total} positions open")
        total_fetched = 0
        while total_fetched < current_stat.total:
            current_page = total_fetched // per_page_size
            result = await client.get_contract_list(
                page_id=current_page,
                page_size=per_page_size,
                margin_coin_name=current_stat.margin_coin_name,
            )
            for current_contract in result.data.orders:
                print(f" - {current_contract}")
            
            await asyncio.sleep(1) # prevent rate limiting
            total_fetched += per_page_size

    await client.aclose()

@pytest.mark.asyncio
@pytest.mark.skipif(True) # remove when check-in is fixed...
async def test_bx_do_daily_check_in():
    client = BXUltraClient()

    # not working
    await client.do_daily_check_in()

    await client.aclose()


@pytest.mark.asyncio
async def test_bx_search_copy_traders():
    client = BXUltraClient()

    result = await client.search_copy_traders(nick_name="Bitcoin2024")

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("Search results: ")
    for current_trader in result.data.result:
        print(f" - {current_trader}")
    
    # get the first trader's positions
    if result.data.result:
        first_trader = result.data.result[0]
        trader_positions = await client.get_copy_trade_trader_positions(
            uid=first_trader.get_uid(),
            api_identity=first_trader.get_api_identity(),
        )

        print(f"Trader {first_trader.get_nick_name()}'s positions: ")
        for current_position in trader_positions.data.positions:
            print(f" - {current_position}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_copy_trade_trader_positions():
    client = BXUltraClient()

    result = await client.get_copy_trade_trader_positions(
        uid=1139467159170899972,
        api_identity=1146548274759884800,
        # uid=1139467159170900000,
        # api_identity=1146548274759884800,
    )

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("User's positions: ")
    for current_position in result.data.positions:
        print(f" - {current_position}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_hint_list():
    client = BXUltraClient()

    result = await client.get_hint_list()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print("hints:")
    for current_hint in result.data:
        print(f" - {current_hint}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_zendesk_ab_status():
    client = BXUltraClient()

    result = await client.get_zendesk_ab_status()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    print(f"ab status: {result.data.ab_status}")

    await client.aclose()

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
    assert result.code == 0

    print(f"Total amount: {result.data.total}")

    await client.aclose()

@pytest.mark.asyncio
async def test_bx_get_homepage():
    client = BXUltraClient()

    result = await client.get_homepage()

    assert result is not None
    assert result.code == 0
    assert result.data is not None

    await client.aclose()






