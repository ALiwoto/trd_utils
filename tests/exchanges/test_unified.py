import pytest
import asyncio

from trd_utils.exchanges import (
    BXUltraClient,
    BlofinClient,
    HyperLiquidClient,
)

from trd_utils.exchanges.base_types import UnifiedPositionInfo
from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.exchanges.okx.okx_client import OkxClient
from trd_utils.exchanges.price_fetcher import IPriceFetcher
from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

unified_test1_targets = {
    "okx": [
        "2B6BDA00968EA9F8",
    ],
    "hyperliquid": [
        "0xefd3ab65915e35105caa462442c9ecc1346728df",
    ],
    "blofin": [
        2897425892,
    ],
    "bx": [
        # 1023995029120749569, hidden positions
        # 1998800000051548, has identity
        # 1998800000051839,
        1414050434086264836,
        1355383321879420928,
    ],
}


def initialize_clients() -> dict[str, ExchangeBase]:
    result = {
        "bx": BXUltraClient(),
        "blofin": BlofinClient(),
        "hyperliquid": HyperLiquidClient(),
        "okx": OkxClient(),
    }

    # if initialization requires more things to be done, do it here

    return result


async def cleanup_clients(all_clients: dict[str, ExchangeBase]) -> None:
    for client in all_clients.values():
        await client.aclose()


pairs_for_last_candle = ["BTC/USDT", "ETH/USDT", "XRP/USDT"]

@pytest.mark.asyncio
async def test_get_last_candle():
    all_clients = initialize_clients()
    loop = asyncio.get_running_loop()

    print("fetching last candles...")
    for platform in unified_test1_targets:
        client = all_clients[platform]  # let it fail if KeyError happens
        if not isinstance(client, IPriceFetcher):
            continue

        price_task = loop.create_task(client.do_price_subscribe())
        # wait till the websocket can get some data
        await asyncio.sleep(6)

        for current_pair in pairs_for_last_candle:
            result = await client.get_last_candle(
                pair=current_pair,
            )

            assert result is not None
            # make sure everything is serializable
            _ = type(result).deserialize(result.serialize())

            print(f"last candle of {current_pair}: {result}")

        price_task.cancel()

    # make sure the price tasks are destroyed properly before exiting
    await asyncio.sleep(2)
    await cleanup_clients(
        all_clients=all_clients,
    )


@pytest.mark.asyncio
async def test_unified_get_trader_positions1():
    all_clients = initialize_clients()

    for platform in unified_test1_targets:
        client = all_clients[platform]  # let it fail if KeyError happens

        for target in unified_test1_targets[platform]:
            result = await client.get_unified_trader_positions(
                uid=target,
            )

            assert result is not None

            # make sure everything is serializable
            _ = type(result).deserialize(result.serialize())

            for position in result.positions:
                print(f"({target}): current position: {position}")
    await cleanup_clients(
        all_clients=all_clients,
    )


@pytest.mark.asyncio
async def test_unified_get_trader_info():
    all_clients = initialize_clients()

    for platform in unified_test1_targets:
        client = all_clients[platform]  # let it fail if KeyError happens

        for target in unified_test1_targets[platform]:
            result = await client.get_unified_trader_info(
                uid=target,
            )

            assert result is not None

            # make sure everything is serializable
            _ = type(result).deserialize(result.serialize())

            print(f"({platform}) Trader info for {target}: {result}")
    await cleanup_clients(
        all_clients=all_clients,
    )


def test_unified_serialization():
    pos = UnifiedPositionInfo()
    pos.initial_margin = 1000

    result = pos.serialize()
    print(result)

    my_pos = UnifiedPositionInfo.deserialize(result)

    assert my_pos.initial_margin == pos.initial_margin
