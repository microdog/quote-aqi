import base64
import io
import sys
from datetime import datetime

from loguru import logger
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random

from quote_aqi.caiyunapp import CaiYunClientV26, HourlyResponse
from quote_aqi.config import Settings
from quote_aqi.mindreset import DotClient, ImageAPIRequest
from quote_aqi.models import AQIPoint
from quote_aqi.plot import PlotData, plot_quote0
from quote_aqi.standards import AQIStandardChina, AQIStandardUSA


def _config_logging(log_level: str):
    logger.remove()
    logger.add(sys.stderr, level=log_level)


def _load_settings() -> Settings:
    try:
        return Settings()  # pyright: ignore[reportCallIssue]
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        sys.exit(1)


def retrieve_aqi_data(settings: Settings) -> HourlyResponse:
    client = CaiYunClientV26(settings.caiyun_app_key, settings.caiyun_app_secret)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=3))
    def _get_hourly() -> HourlyResponse:
        return client.get_hourly((settings.longitude, settings.latitude))

    try:
        response = _get_hourly()
        logger.debug("AQI data: {response}", response=response)
    except Exception as e:
        logger.error(f"Failed to retrieve AQI data: {e}")
        sys.exit(1)
    return response


def generate_plot_data(settings: Settings, aqi_data: HourlyResponse) -> PlotData:
    std_us = AQIStandardUSA()
    std_cn = AQIStandardChina()

    points = []
    for api, pm25 in zip(
        aqi_data.result.hourly.air_quality.aqi, aqi_data.result.hourly.air_quality.pm25
    ):
        timestamp = datetime.fromisoformat(api.datetime)
        points.append(
            AQIPoint(
                timestamp=timestamp,
                aqi_chn=api.value.chn,
                aqi_usa=api.value.usa,
                description_chn=std_cn.evaluate(api.value.chn).category,
                description_usa=std_us.evaluate(api.value.usa).category,
                pm25=pm25.value,
            )
        )

    plot_data = PlotData(
        poi=settings.poi,
        realtime=points[0],
        forecast=points[1:],
    )
    logger.debug("Plot data: {plot_data}", plot_data=plot_data)
    return plot_data


def generate_image(plot_data: PlotData) -> Image.Image:
    return plot_quote0(plot_data)


def upload_image(settings: Settings, image: Image.Image):
    dot_client = DotClient(settings.dot_api_key)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    request = ImageAPIRequest(
        deviceId=settings.dot_quote0_device_id,
        image=image_base64,
        link=settings.dot_quote0_link,
        border=ImageAPIRequest.Border.WHITE,
        dither_type=ImageAPIRequest.DitherType.NONE,
    )
    try:
        response = dot_client.image_api(request)
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        sys.exit(1)
    else:
        logger.info(f"Image uploaded successfully: {response.message}")


def main(log_level: str = "INFO"):
    _config_logging(log_level)

    settings = _load_settings()

    aqi_data = retrieve_aqi_data(settings)
    plot_data = generate_plot_data(settings, aqi_data)
    image = generate_image(plot_data)
    upload_image(settings, image)
