import pytest
# import asyncio

from trd_utils.exchanges import BlofinClient

from trd_utils.types_helper import base_model

# since we are testing, performance overhead of UltraList is not a concern
base_model.ULTRA_LIST_ENABLED = True

@pytest.mark.asyncio
async def test_bx_get_earning_amounts():
    client = BlofinClient()

    print(client) #TODO