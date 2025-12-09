import base64
from datetime import datetime

from icecream import ic

from quote_aqi.caiyunapp import CaiYunClientV26
from quote_aqi.config import Settings
from quote_aqi.models import AQIPoint
from quote_aqi.plot import PlotData, plot_quote0
from quote_aqi.standards import AQIStandardChina, AQIStandardUSA

settings = Settings()  # pyright: ignore[reportCallIssue]

ic(settings)

client = CaiYunClientV26(settings.caiyun_app_key, settings.caiyun_app_secret)
response = client.get_hourly((settings.longitude, settings.latitude))
print(response)

std_us = AQIStandardUSA()
std_cn = AQIStandardChina()


points = []
for api, pm25 in zip(
    response.result.hourly.air_quality.aqi, response.result.hourly.air_quality.pm25
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

ic(points)


plot_data = PlotData(
    poi=settings.poi,
    realtime=points[0],
    forecast=points[1:],
)
image = plot_quote0(plot_data)
image.save("quote0.png")
image.show()

with open("quote0.png", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()
    print(encoded)
