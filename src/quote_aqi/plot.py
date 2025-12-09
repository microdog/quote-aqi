from dataclasses import dataclass
from datetime import datetime, timedelta

from PIL import Image, ImageDraw

from quote_aqi import fonts
from quote_aqi.models import AQIPoint
from quote_aqi.utils import draw_text_psd_style, round_half_hour


@dataclass
class PlotData:
    poi: str
    realtime: AQIPoint
    forecast: list[AQIPoint]


QUOTE0_WIDTH = 296
QUOTE0_HEIGHT = 152
QUOTE0_MODE = "L"  # 8-bit grayscale
QUOTE0_BG_COLOR = 255

FONT_SARASA_UI_SC_BOLD = {
    16: fonts.load_font(fonts.FONT_SARASA_UI_SC_BOLD, 16),
    30: fonts.load_font(fonts.FONT_SARASA_UI_SC_BOLD, 30),
    60: fonts.load_font(fonts.FONT_SARASA_UI_SC_BOLD, 60),
}


def plot_quote0(plot_data: PlotData) -> Image.Image:
    canvas = Image.new(QUOTE0_MODE, (QUOTE0_WIDTH, QUOTE0_HEIGHT), QUOTE0_BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    draw.fontmode = "1"

    now_time = round_half_hour(plot_data.realtime.timestamp).strftime("%H:%M")
    draw.text(
        (10, 6),
        f"{plot_data.poi} 当前 {now_time} AQI (CN/US)",
        fill=0,
        font=FONT_SARASA_UI_SC_BOLD[16],
    )
    draw_text_psd_style(
        draw,
        (10, 20),
        f"{plot_data.realtime.aqi_chn} / {plot_data.realtime.aqi_usa}",
        fill=0,
        font=FONT_SARASA_UI_SC_BOLD[60],
        tracking=-50,
    )
    draw_text_psd_style(
        draw,
        (10, 86),
        f"{plot_data.realtime.description_chn} / {plot_data.realtime.description_usa}",
        fill=0,
        font=FONT_SARASA_UI_SC_BOLD[30],
        tracking=-50,
    )

    forecast_line = "未来 "
    for forecast in plot_data.forecast[:3]:
        forecast_line += f"  {forecast.aqi_chn}/{forecast.aqi_usa}"
    draw.text((10, 128), forecast_line, fill=0, font=FONT_SARASA_UI_SC_BOLD[16])

    return canvas


if __name__ == "__main__":
    plot_data = PlotData(
        poi="徐汇区",
        realtime=AQIPoint(
            timestamp=datetime.now(),
            aqi_chn=300,
            aqi_usa=300,
            description_chn="严重",
            description_usa="对敏感人群有害",
            pm25=100,
        ),
        forecast=[
            AQIPoint(
                timestamp=datetime.now() + timedelta(hours=1),
                aqi_chn=100,
                aqi_usa=100,
                description_chn="良",
                description_usa="良",
                pm25=100,
            ),
            AQIPoint(
                timestamp=datetime.now() + timedelta(hours=2),
                aqi_chn=100,
                aqi_usa=100,
                description_chn="良",
                description_usa="良",
                pm25=100,
            ),
            AQIPoint(
                timestamp=datetime.now() + timedelta(hours=3),
                aqi_chn=100,
                aqi_usa=100,
                description_chn="良",
                description_usa="良",
                pm25=100,
            ),
        ],
    )
    image = plot_quote0(plot_data)
    image.save("quote0.png")
    image.show()

    import base64

    with open("quote0.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        print(encoded)
