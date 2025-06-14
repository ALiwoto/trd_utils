
from decimal import Decimal
import json
import logging
from typing import Type
import httpx

from pathlib import Path

from trd_utils.cipher import AESCipher
from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.exchanges.hyperliquid.hyperliquid_types import HyperLiquidApiResponse, TraderPositionsInfoResponse

logger = logging.getLogger(__name__)


class HyperLiquidClient(ExchangeBase):
    ###########################################################
    # region client parameters
    hyperliquid_api_base_host: str = "https://api.hyperliquid.xyz"
    hyperliquid_api_base_url: str = "https://api.hyperliquid.xyz"
    origin_header: str = "app.hyperliquid.xy"

    # endregion
    ###########################################################
    # region client constructor
    def __init__(
        self,
        account_name: str = "default",
        http_verify: bool = True,
        fav_letter: str = "^",
        read_session_file: bool = False,
        sessions_dir: str = "sessions",
        use_http1: bool = True,
        use_http2: bool = False,
    ):
        # it looks like hyperliquid's api endpoints don't support http2 :(
        self.httpx_client = httpx.AsyncClient(
            verify=http_verify,
            http1=use_http1,
            http2=use_http2,
        )
        self.account_name = account_name
        self._fav_letter = fav_letter
        self.sessions_dir = sessions_dir

        if read_session_file:
            self.read_from_session_file(f"{sessions_dir}/{self.account_name}.hl")

    # endregion
    ###########################################################
    # region info endpoints
    async def get_trader_positions_info(
        self,
        uid: int | str,
    ) -> TraderPositionsInfoResponse:
        payload = {
            "type": "clearinghouseState",
            "user": f"{uid}",
        }
        headers = self.get_headers()
        return await self.invoke_post(
            f"{self.hyperliquid_api_base_host}/info",
            headers=headers,
            content=payload,
            model=TraderPositionsInfoResponse,
        )

    #endregion
    ###########################################################
    # region another-thing
    # async def get_another_thing_info(self, uid: int) -> AnotherThingInfoResponse:
    #     payload = {
    #         "uid": uid,
    #     }
    #     headers = self.get_headers()
    #     return await self.invoke_post(
    #         f"{self.hyperliquid_api_base_url}/another-thing/info",
    #         headers=headers,
    #         content=payload,
    #         model=CopyTraderInfoResponse,
    #     )

    # endregion
    ###########################################################
    # region client helper methods
    def get_headers(self, payload=None, needs_auth: bool = False) -> dict:
        the_headers = {
            # "Host": self.hyperliquid_api_base_host,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": self.user_agent,
            "Connection": "close",
            "appsiteid": "0",
        }

        if self.x_requested_with:
            the_headers["X-Requested-With"] = self.x_requested_with

        if needs_auth:
            the_headers["Authorization"] = f"Bearer {self.authorization_token}"
        return the_headers

    def read_from_session_file(self, file_path: str) -> None:
        """
        Reads from session file; if it doesn't exist, creates it.
        """
        # check if path exists
        target_path = Path(file_path)
        if not target_path.exists():
            return self._save_session_file(file_path=file_path)

        aes = AESCipher(key=f"bf_{self.account_name}_bf", fav_letter=self._fav_letter)
        content = aes.decrypt(target_path.read_text()).decode("utf-8")
        json_data: dict = json.loads(content)

        self.authorization_token = json_data.get(
            "authorization_token",
            self.authorization_token,
        )
        self.user_agent = json_data.get("user_agent", self.user_agent)

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """

        json_data = {
            "authorization_token": self.authorization_token,
            "user_agent": self.user_agent,
        }
        aes = AESCipher(key=f"bf_{self.account_name}_bf", fav_letter=self._fav_letter)
        target_path = Path(file_path)
        target_path.write_text(aes.encrypt(json.dumps(json_data)))

    # endregion
    ###########################################################
