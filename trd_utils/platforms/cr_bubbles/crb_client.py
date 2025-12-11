import httpx

from trd_utils.http_utils import HttpAsyncClientBase
from trd_utils.platforms.cr_bubbles.crb_types import BubblesTop1kCollection


class CrBubblesClient(HttpAsyncClientBase):
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )
    base_url: str = "https://cryptobubbles.net"
    timeout: float = 12.0

    def __init__(
        self,
        timeout: float = 12.0,
    ) -> None:
        self.timeout = timeout
        self.httpx_client = httpx.AsyncClient(
            headers={
                "User-Agent": self.user_agent,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": f"{self.base_url}/",
                "Priority": "u=1, i",
                "Sec-Ch-Ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Accept-Encoding": "gzip, deflate, br, zstd",
            },
            timeout=httpx.Timeout(self.timeout, connect=self.timeout / 2),
        )

    def get_platform_name(self) -> str:
        return "crb"

    async def get_top_1k(self) -> BubblesTop1kCollection:
        data = await self.invoke_get(
            url=f"{self.base_url}/backend/data/bubbles1000.usd.json",
            raw_data=False,
            model_type=None,
        )
        if not isinstance(data, list):
            raise ValueError(f"unexpected response data format: {type(data)}")

        return BubblesTop1kCollection(
            **{
                "data": data,
            }
        )

    async def aclose(self) -> None:
        if self.httpx_client:
            await self.httpx_client.aclose()
            self.httpx_client = None

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        await self.aclose()
