"""BingxUltra exchange subclass"""

from decimal import Decimal
import json
import logging
import uuid

import httpx

import time
from pathlib import Path

from .common_utils import do_ultra_ss
from .bx_types import ZoneModuleListResponse
from ..cipher import AESCipher

PLATFORM_ID_ANDROID = "10"
PLATFORM_ID_WEB = "30"

ANDROID_DEVICE_BRAND = "SM-N976N"
WEB_DEVICE_BRAND = "Windows 10_Chrome_127.0.0.0"

ANDROID_APP_VERSION = "4.28.3"
WEB_APP_VERSION = "4.78.12"

logger = logging.getLogger(__name__)


class BXUltraClient:
    we_api_base_host: str = "\u0061pi-\u0061pp.w\u0065-\u0061pi.com"
    we_api_base_url: str = "https://\u0061pi-\u0061pp.w\u0065-\u0061pi.com/\u0061pi"

    device_id: str = None
    trace_id: str = None
    app_version: str = "4.28.3"
    platform_id: str = "10"
    install_channel: str = "officialAPK"
    channel_header: str = "officialAPK"
    authorization_token: str = None
    app_id: str = "30004"
    trade_env: str = "real"
    timezone: str = "3"
    os_version: str = "7.1.2"
    device_brand: str = "SM-N976N"
    platform_lang: str = "en"
    sys_lang: str = "en"
    user_agent: str = "okhttp/4.12.0"
    httpx_client: httpx.AsyncClient = None
    account_name: str = "default"

    _fav_letter: str = "^"

    def __init__(
        self,
        account_name: str = "default",
        platform_id: str = PLATFORM_ID_ANDROID,
        device_brand: str = ANDROID_DEVICE_BRAND,
        app_version: str = ANDROID_APP_VERSION,
    ):
        self.httpx_client = httpx.AsyncClient(verify=False)
        self.account_name = account_name
        self.platform_id = platform_id
        self.device_brand = device_brand
        self.app_version = app_version

        self.read_from_session_file(f"{self.account_name}.bx")

    async def get_zone_module_info(
        self,
        only_one_position: int = 0,
        biz_type: int = 10
    ) -> ZoneModuleListResponse:
        """
        Fetches and returns zone module info from the API.
        Available zones are: All, Forex, Indices, MEME, Elon-inspired,
        Innovation, AI Agent, BTC Ecosystem, TON Ecosystem, Commodities,
        GameFi, Fan Tokens , Layer1 & Layer2, SOL Ecosystem, RWA, LST, DePin, AI
        """
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/coin/v1/zone/module-info",
            headers=headers,
            params=params,
        )
        return ZoneModuleListResponse.deserialize(response.json(parse_float=Decimal))

    async def get_user_favorite_quotation(
        self, only_one_position: int = 0, biz_type: int = 1
    ):
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/coin/v1/user/favorite/quotation",
            headers=headers,
            params=params,
        )
        return response.json()

    async def get_quotation_rank(self, only_one_position: int = 0, order_flag: int = 0):
        params = {
            "orderFlag": f"{order_flag}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/coin/v1/rank/quotation-rank",
            headers=headers,
            params=params,
        )
        return response.json()

    async def get_hot_search(self, only_one_position: int = 0, biz_type: int = 30):
        params = {
            "bizType": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/coin/v1/quotation/hot-search",
            headers=headers,
            params=params,
        )
        return response.json()

    async def get_homepage(self, only_one_position: int = 0, biz_type: int = 30):
        params = {
            "biz-type": f"{biz_type}",
        }
        headers = self.get_headers(params)
        headers["Only_one_position"] = f"{only_one_position}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/coin/v1/discovery/homepage",
            headers=headers,
            params=params,
        )
        return response.json()

    async def get_assets_info(self):
        headers = self.get_headers()
        headers["Authorization"] = f"Bearer {self.authorization_token}"
        response = await self.httpx_client.get(
            f"{self.we_api_base_url}/asset-manager/v1/assets/account-total-overview",
            headers=headers,
        )
        return response.json()

    def get_headers(self, payload=None) -> dict:
        the_timestamp = int(time.time() * 1000)
        return {
            "Host": self.we_api_base_host,
            "Content-Type": "application/json",
            "Mainappid": "10009",
            "Accept": "application/json",
            "Origin": "https://bingx.com",
            "Traceid": self.trace_id,
            "App_version": self.app_version,
            "Platformid": self.platform_id,
            "Device_id": self.device_id,
            "Device_brand": self.device_brand,
            "Channel": self.channel_header,
            "Appid": self.app_id,
            "Trade_env": self.trade_env,
            "Timezone": self.timezone,
            "Lang": self.platform_lang,
            "Syslang": self.sys_lang,
            "Sign": do_ultra_ss(
                e_param=None,
                se_param=None,
                le_param=None,
                timestamp=the_timestamp,
                trace_id=self.trace_id,
                device_id=self.device_id,
                platform_id=self.platform_id,
                app_version=self.app_version,
                payload_data=payload,
            ),
            "Timestamp": f"{the_timestamp}",
            # 'Accept-Encoding': 'gzip, deflate',
            "User-Agent": self.user_agent,
            "Connection": "close",
        }

    async def aclose(self) -> None:
        await self.httpx_client.aclose()
        logger.info("BXUltraClient closed")
        return True

    def read_from_session_file(self, file_path: str) -> None:
        """
        Reads from session file; if it doesn't exist, creates it.
        """
        # check if path exists
        target_path = Path(file_path)
        if not target_path.exists():
            return self._save_session_file(file_path=file_path)

        aes = AESCipher(key=f"bx_{self.account_name}_bx", fav_letter=self._fav_letter)
        content = aes.decrypt(target_path.read_text()).decode("utf-8")
        json_data: dict = json.loads(content)

        self.device_id = json_data.get("device_id", self.device_id)
        self.trace_id = json_data.get("trace_id", self.trace_id)
        self.app_version = json_data.get("app_version", self.app_version)
        self.platform_id = json_data.get("platform_id", self.platform_id)
        self.install_channel = json_data.get("install_channel", self.install_channel)
        self.channel_header = json_data.get("channel_header", self.channel_header)
        self.authorization_token = json_data.get(
            "authorization_token", self.authorization_token
        )
        self.app_id = json_data.get("app_id", self.app_id)
        self.trade_env = json_data.get("trade_env", self.trade_env)
        self.timezone = json_data.get("timezone", self.timezone)
        self.os_version = json_data.get("os_version", self.os_version)
        self.device_brand = json_data.get("device_brand", self.device_brand)
        self.platform_lang = json_data.get("platform_lang", self.platform_lang)
        self.sys_lang = json_data.get("sys_lang", self.sys_lang)
        self.user_agent = json_data.get("user_agent", self.user_agent)

    def _save_session_file(self, file_path: str) -> None:
        """
        Saves current information to the session file.
        """
        if not self.device_id:
            self.device_id = uuid.uuid4().hex.replace("-", "") + "##"

        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex.replace("-", "")

        json_data = {
            "device_id": self.device_id,
            "trace_id": self.trace_id,
            "app_version": self.app_version,
            "platform_id": self.platform_id,
            "install_channel": self.install_channel,
            "channel_header": self.channel_header,
            "authorization_token": self.authorization_token,
            "app_id": self.app_id,
            "trade_env": self.trade_env,
            "timezone": self.timezone,
            "os_version": self.os_version,
            "device_brand": self.device_brand,
            "platform_lang": self.platform_lang,
            "sys_lang": self.sys_lang,
            "user_agent": self.user_agent,
        }
        aes = AESCipher(key=f"bx_{self.account_name}_bx", fav_letter=self._fav_letter)
        target_path = Path(file_path)
        target_path.write_text(aes.encrypt(json.dumps(json_data)))
