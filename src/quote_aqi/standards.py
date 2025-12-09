from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class AQIEvaluation:
    category: str


class AQIStandard:
    @abstractmethod
    def evaluate(self, aqi: int) -> AQIEvaluation:
        pass


class AQIStandardUSA(AQIStandard):
    def evaluate(self, aqi: int) -> AQIEvaluation:
        if aqi <= 50:
            return AQIEvaluation(category="良好")
        elif aqi <= 100:
            return AQIEvaluation(category="中等")
        elif aqi <= 150:
            return AQIEvaluation(category="对敏感人群有害")
        elif aqi <= 200:
            return AQIEvaluation(category="不健康")
        elif aqi <= 300:
            return AQIEvaluation(category="极不健康")
        else:
            return AQIEvaluation(category="有毒害")


class AQIStandardChina(AQIStandard):
    def evaluate(self, aqi: int) -> AQIEvaluation:
        if aqi <= 50:
            return AQIEvaluation(category="优")
        elif aqi <= 100:
            return AQIEvaluation(category="良")
        elif aqi <= 150:
            return AQIEvaluation(category="轻度")
        elif aqi <= 200:
            return AQIEvaluation(category="中度")
        elif aqi <= 300:
            return AQIEvaluation(category="重度")
        else:
            return AQIEvaluation(category="严重")
