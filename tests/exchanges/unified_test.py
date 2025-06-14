import pytest

from trd_utils.exchanges import (
    BXUltraClient,
    BlofinClient,
    HyperLiquidClient,
)

from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

unified_test1_targets = {
    "hyperliquid": [
        "0xefd3ab65915e35105caa462442c9ecc1346728df",
    ],
    "blofin": [
        2897425892,
    ],
    "bx": [
        # 1023995029120749569, hidden positions
        1414050434086264836,
    ]
}

def initialize_clients() -> dict[str, ExchangeBase]:
    result = {
        "bx": BXUltraClient(),
        "blofin": BlofinClient(),
        "hyperliquid": HyperLiquidClient(),
    }

    # if initialization requires more things to be done, do it here

    return result

async def cleanup_clients(all_clients: dict[str, ExchangeBase]) -> None:
    for client in all_clients.values():
        await client.aclose()

@pytest.mark.asyncio
async def test_unified_get_trader_positions1():
    all_clients = initialize_clients()
    
    for platform in unified_test1_targets:
        client = all_clients[platform] # let it fail if KeyError happens
        
        for target in unified_test1_targets[platform]:
            result = await client.get_unified_trader_positions(
                uid=target,
            )

            assert result is not None

            # make sure everything is serializable
            _ = type(result).deserialize(result.serialize())

            for position in result.positions:
                print(f"current position: {position}")
    await cleanup_clients(
        all_clients=all_clients,
    )


@pytest.mark.asyncio
async def test_unified_get_trader_info():
    all_clients = initialize_clients()
    
    for platform in unified_test1_targets:
        client = all_clients[platform] # let it fail if KeyError happens
        
        for target in unified_test1_targets[platform]:
            result = await client.get_unified_trader_info(
                uid=target,
            )

            assert result is not None

            # make sure everything is serializable
            _ = type(result).deserialize(result.serialize())

            print(f"Trader info for {target}: {result}")
    await cleanup_clients(
        all_clients=all_clients,
    )
    
