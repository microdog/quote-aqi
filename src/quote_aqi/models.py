
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AQIPoint:
    timestamp: datetime
    aqi_chn: int
    aqi_usa: int
    description_chn: str
    description_usa: str
    pm25: int
