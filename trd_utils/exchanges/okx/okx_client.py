import json
import logging
import time
import httpx

from pathlib import Path

from trd_utils.cipher import AESCipher
from trd_utils.exchanges.base_types import (
    UnifiedPositionInfo,
    UnifiedTraderInfo,
    UnifiedTraderPositions,
)
from trd_utils.exchanges.exchange_base import ExchangeBase
from trd_utils.exchanges.okx.okx_types import (
    AppContextUserInfo,
    CurrentUserPositionsResponse,
    UserInfoHtmlParser,
    UserInfoInitialProps,
)

logger = logging.getLogger(__name__)

BASE_PROFILE_URL = "https://www.okx.com/copy-trading/account/"


class OkxClient(ExchangeBase):
    ###########################################################
    # region client parameters
    okx_api_base_host: str = "https://www.okx.com"
    okx_api_base_url: str = "https://www.okx.com"
    okx_api_v5_url: str = "https://www.okx.com/priapi/v5"
    origin_header: str = "https://www.okx.com"

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
        self.exchange_name = "okx"

        super().__init__()

        if read_session_file:
            self.read_from_session_file(f"{sessions_dir}/{self.account_name}.okx")

    # endregion
    ###########################################################
    # region positions endpoints
    async def get_trader_positions(
        self,
        uid: int | str,
    ) -> CurrentUserPositionsResponse:
        params = {
            "uniqueName": f"{uid}",
            "t": f"{int(time.time() * 1000)}",
        }
        headers = self.get_headers()
        return await self.invoke_get(
            f"{self.okx_api_v5_url}/ecotrade/public/community/user/position-current",
            headers=headers,
            params=params,
            model_type=CurrentUserPositionsResponse,
        )

    # endregion
    ###########################################################
    # region another-thing

    async def get_copy_trader_info(
        self,
        uid: int | str,
    ) -> UserInfoInitialProps:
        params = {
            "tab": "trade",
        }
        headers = self.get_headers()
        result: bytes = await self.invoke_get(
            f"{self.okx_api_base_host}/copy-trading/account/{uid}",
            headers=headers,
            params=params,
            model_type=AppContextUserInfo,
            raw_data=True,
        )
        parser = UserInfoHtmlParser("__app_data_for_ssr__")
        parser.feed(result.decode("utf-8"))
        if not parser.found_value:
            raise ValueError("Okx API returned invalid response")

        return AppContextUserInfo(
            **(json.loads(parser.found_value)["appContext"]),
        ).initial_props

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
        if not target_path.exists():
            target_path.mkdir(parents=True)
        target_path.write_text(aes.encrypt(json.dumps(json_data)))

    # endregion
    ###########################################################
    # region unified methods
    async def get_unified_trader_positions(
        self,
        uid: int | str,
    ) -> UnifiedTraderPositions:
        result = await self.get_trader_positions(
            uid=uid,
        )
        unified_result = UnifiedTraderPositions()
        unified_result.positions = []
        for position in result.data[0].pos_data:
            unified_pos = UnifiedPositionInfo()
            unified_pos.position_id = position.pos_id
            unified_pos.position_pnl = round(position.realized_pnl, 3)
            unified_pos.position_side = position.get_side()
            unified_pos.margin_mode = position.mgn_mode
            unified_pos.position_leverage = position.lever
            unified_pos.position_pair = position.get_pair()
            unified_pos.open_time = position.c_time
            unified_pos.open_price = position.avg_px
            unified_pos.open_price_unit = position.quote_ccy
            unified_pos.initial_margin = position.margin
            unified_result.positions.append(unified_pos)

        return unified_result

    async def get_unified_trader_info(
        self,
        uid: int | str,
    ) -> UnifiedTraderInfo:
        result = await self.get_copy_trader_info(
            uid=uid,
        )
        account_info = result.pre_process.leader_account_info
        overview = result.overview_data

        unified_info = UnifiedTraderInfo()
        unified_info.trader_id = account_info.unique_name or uid
        unified_info.trader_name = account_info.en_nick_name or account_info.nick_name
        unified_info.trader_url = f"{BASE_PROFILE_URL}{uid}"
        unified_info.win_rate = overview.win_rate

        return unified_info

    # endregion
    ###########################################################
