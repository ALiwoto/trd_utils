import time
import pytest

# import asyncio
from trd_utils.platforms import CrBubblesClient
from trd_utils.types_helper import base_model

LOCAL_PROXY_URL = "http://localhost:4141"

base_model.ULTRA_LIST_ENABLED = True

async def timed_get_top_1k(client: CrBubblesClient):
    start = time.perf_counter()
    result = await client.get_top_1k()
    elapsed = time.perf_counter() - start
    print(f"calling 'get_top_1k' took {elapsed:.3f}s")
    return result

@pytest.mark.asyncio
async def test_crb_get_top_1k_bubbles():
    async with CrBubblesClient() as client:
        client.set_proxy_base_url(LOCAL_PROXY_URL)
        if await client.is_proxy_available():
            print(f"using proxy url: {LOCAL_PROXY_URL}")

            # the proxy server should cache the response, so subsequent calls should be faster
            result = await timed_get_top_1k(client)
            result = await timed_get_top_1k(client)
            result = await timed_get_top_1k(client)
            result = await timed_get_top_1k(client)
        else:
            client.set_proxy_base_url(None)

        result = await timed_get_top_1k(client)

        assert result is not None

        print(f"total bubbles: {len(result.data)}")

        for current in result.data[:10]:
            print(current)
            print(f"hour: {current.get_hourly_change()}")

        pepe_info = result.try_find_by_symbol("kPEPE")
        assert pepe_info is not None
        print(f"found bubble by symbol 'kPEPE': {pepe_info}")

        pepe_info = result.try_find_by_symbol("K" + "PEPE")
        assert pepe_info is not None
        print(f"found bubble by symbol 'kPEPE': {pepe_info}")
