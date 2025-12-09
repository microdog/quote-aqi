import base64
import hashlib
import hmac
import time
import urllib.parse
import uuid

import requests
from pydantic import BaseModel

Longitude = float
Latitude = float
Location = tuple[Longitude, Latitude]


class RealtimeData(BaseModel):
    class AirQuality(BaseModel):
        class AQI(BaseModel):
            chn: int
            usa: int

        class Description(BaseModel):
            chn: str
            usa: str

        pm25: int
        pm10: int
        aqi: AQI
        description: Description

    status: str
    air_quality: AirQuality


class HourlyData(BaseModel):
    class AirQuality(BaseModel):
        class AQI(BaseModel):
            class Value(BaseModel):
                chn: int
                usa: int

            datetime: str
            value: Value

        class PM25(BaseModel):
            datetime: str
            value: int

        aqi: list[AQI]
        pm25: list[PM25]

    status: str
    air_quality: AirQuality


class WeatherResponse(BaseModel):
    class Result(BaseModel):
        realtime: RealtimeData
        hourly: HourlyData

    status: str
    server_time: int
    result: Result


class HourlyResponse(BaseModel):
    class Result(BaseModel):
        hourly: HourlyData

    status: str
    server_time: int
    result: Result


class CaiYunClientV26:
    BASE_URL = "https://api.caiyunapp.com"
    PATH_PREFIX = "/v2.6"

    def __init__(self, app_key: str, app_secret: str, timeout: float = 10):
        self.app_key = app_key
        self.app_secret = app_secret
        self.path_prefix = self.PATH_PREFIX + "/" + app_key
        self.base_url = self.BASE_URL + self.path_prefix
        self.session = requests.Session()
        self.timeout = timeout

    def _sign(
        self, method: str, path: str, nonce: str, timestamp: str, query: dict[str, str]
    ) -> str:
        # 1. 对 query 参数按字母顺序排序
        sorted_keys = sorted(query.keys())

        # 2. 构建 query 字符串（URL 编码）
        query_parts = []
        for k in sorted_keys:
            encoded_key = urllib.parse.quote(k)
            encoded_value = urllib.parse.quote(query[k])
            query_parts.append(f"{encoded_key}={encoded_value}")
        query_str = "&".join(query_parts)

        # 3. 构建签名字符串
        string_to_sign = ":".join(
            [method, path, query_str, self.app_key, nonce, timestamp]
        )

        # 4. 使用 HMAC-SHA256 计算签名
        h = hmac.new(
            self.app_secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        )

        # 5. Base64 编码（URL 安全）
        signature = base64.urlsafe_b64encode(h.digest()).decode("utf-8")

        return signature

    def _request(
        self, method: str, path: str, query: dict[str, str]
    ) -> requests.Response:
        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time()))
        signature = self._sign(method, self.path_prefix + path, nonce, timestamp, query)
        url = self.base_url + path
        headers = {
            "x-cy-nonce": nonce,
            "x-cy-timestamp": timestamp,
            "x-cy-signature": signature,
        }
        response = self.session.request(
            method, url, headers=headers, params=query, timeout=self.timeout
        )
        response.raise_for_status()
        return response

    def _get(self, path: str, query: dict[str, str]) -> requests.Response:
        return self._request("GET", path, query)

    def get_weather(self, location: Location, hourlysteps=4) -> WeatherResponse:
        query = {
            "hourlysteps": str(hourlysteps),
        }
        response = self._get(f"/{location[0]},{location[1]}/weather", query)
        return WeatherResponse.model_validate_json(response.content)

    def get_hourly(self, location: Location, hourlysteps=4) -> HourlyResponse:
        query = {
            "hourlysteps": str(hourlysteps),
        }
        response = self._get(f"/{location[0]},{location[1]}/hourly", query)
        return HourlyResponse.model_validate_json(response.content)
