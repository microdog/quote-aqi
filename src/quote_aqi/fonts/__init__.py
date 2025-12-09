from pathlib import Path

from PIL import ImageFont

_FONT_DIR = Path(__file__).parent

FONT_SARASA_UI_SC_BOLD = _FONT_DIR / "SarasaUiSC-Bold.ttf"


def load_font(path: Path, font_size: float = 10) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), font_size)
