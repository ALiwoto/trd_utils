import pytest
# import asyncio

from trd_utils.platforms import CrBubblesClient
from trd_utils.types_helper import base_model

base_model.ULTRA_LIST_ENABLED = True


@pytest.mark.asyncio
async def test_crb_get_top_1k_bubbles():
    async with CrBubblesClient() as client:
        result = await client.get_top_1k()

        assert result is not None

        print(f"total bubbles: {len(result.data)}")

        for current in result.data[:10]:
            print(current)
            print(f"hour: {current.get_hourly_change()}")
