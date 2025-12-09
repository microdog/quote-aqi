from enum import IntEnum, StrEnum

import requests
from pydantic import BaseModel, Field


class ImageAPIRequest(BaseModel):
    class Border(IntEnum):
        WHITE = 0
        BLACK = 1

    class DitherType(StrEnum):
        NONE = "NONE"
        DIFFUSION = "DIFFUSION"
        ORDERED = "ORDERED"

    class DitherKernel(StrEnum):
        THRESHOLD = "THRESHOLD"
        ATKINSON = "ATKINSON"
        BURKES = "BURKES"
        FLOYD_STEINBERG = "FLOYD_STEINBERG"
        SIERRA2 = "SIERRA2"
        STUCKI = "STUCKI"
        JARVIS_JUDICE_NINKE = "JARVIS_JUDICE_NINKE"
        DIFFUSION_ROW = "DIFFUSION_ROW"
        DIFFUSION_COLUMN = "DIFFUSION_COLUMN"
        DIFFUSION_2D = "DIFFUSION_2D"

    refresh_now: bool | None = Field(default=None, serialization_alias="refreshNow")
    deviceId: str = Field(serialization_alias="deviceId")
    image: str
    link: str | None = None
    border: Border | None = None
    dither_type: DitherType | None = Field(
        default=None, serialization_alias="ditherType"
    )
    dither_kernel: DitherKernel | None = Field(
        default=None, serialization_alias="ditherKernel"
    )


class ImageAPIResponse(BaseModel):
    message: str


class DotClient:
    BASE_URL = "https://dot.mindreset.tech"

    def __init__(self, api_key: str, timeout: float = 10):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        self.timeout = timeout

    def image_api(self, request: ImageAPIRequest) -> ImageAPIResponse:
        response = self.session.post(
            f"{self.BASE_URL}/api/open/image",
            json=request.model_dump(exclude_none=True),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return ImageAPIResponse.model_validate_json(response.content)
