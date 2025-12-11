
import json
import urllib.parse
from abc import ABC
from decimal import Decimal
from typing import Type

import httpx

from trd_utils.common_utils.httpx_utils import httpx_resp_to_json
from trd_utils.types_helper.base_model import BaseModel


class HttpAsyncClientBase(ABC):
    httpx_client: httpx.AsyncClient = None
    
    # The base url for the proxy server, if any.
    proxy_base_url: str = None

    def get_platform_name(self) -> str:
        return self.__class__.__name__
    
    
    def set_proxy_base_url(self, proxy_base_url: str) -> None:
        """
        Sets the proxy base url.
        """
        self.proxy_base_url = proxy_base_url.rstrip("/")

    def get_final_url(self, target_url: str) -> str:
        if not self.proxy_base_url:
            return target_url

        parsed_ur = urllib.parse.urlparse(target_url)
        return f"{self.proxy_base_url}/{self.get_platform_name()}{parsed_ur.path}"
    
    async def is_proxy_available(self) -> bool:
        """
        Checks whether the proxy server is available by sending a request to
        /health/ping endpoint.
        """
        if not self.proxy_base_url:
            return False

        try:
            response = await self.httpx_client.get(
                url=f"{self.proxy_base_url}/health/ping",
            )
            if response.status_code != 200:
                return False

            j_obj = httpx_resp_to_json(response=response)
            if not isinstance(j_obj, dict):
                return False
            return j_obj.get("result", False)
        except Exception:
            return False
    
    async def invoke_get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """
        response = await self.httpx_client.get(
            url=self.get_final_url(url),
            headers=headers,
            params=params,
        )
        return self._handle_response(
            response=response,
            model_type=model_type,
            parse_float=parse_float,
            raw_data=raw_data,
        )

    async def invoke_post(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        content: dict | str | bytes = "",
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        """
        Invokes the specific request to the specific url with the specific params and headers.
        """

        if isinstance(content, dict):
            content = json.dumps(content, separators=(",", ":"), sort_keys=True)

        response = await self.httpx_client.post(
            url=self.get_final_url(url),
            headers=headers,
            params=params,
            content=content,
        )
        return self._handle_response(
            response=response,
            model_type=model_type,
            parse_float=parse_float,
            raw_data=raw_data,
        )

    def _handle_response(
        self,
        response: httpx.Response,
        model_type: Type[BaseModel] | None = None,
        parse_float=Decimal,
        raw_data: bool = False,
    ) -> "BaseModel":
        if raw_data:
            return response.content

        j_obj = httpx_resp_to_json(
            response=response,
            parse_float=parse_float,
        )
        if not model_type:
            return j_obj

        return model_type.deserialize(j_obj)

