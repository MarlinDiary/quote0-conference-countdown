from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from conference import Conference, days_left, load_conference


WIDTH = 296
HEIGHT = 152
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _fitted_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int):
    for size in range(start, minimum - 1, -1):
        font = _font(size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
    return _font(minimum)


def _centered(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    draw.text(((WIDTH - width) / 2, y - box[1]), text, font=font, fill=fill)


def render_conference(conference: Conference, *, now=None) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((10, 8, WIDTH - 10, 43), radius=8, fill="black")
    name_font = _fitted_font(draw, conference.name, WIDTH - 36, start=25, minimum=14)
    _centered(draw, 13, conference.name, name_font, "white")

    remaining = days_left(conference, now=now)
    if remaining is None:
        passed_font = _fitted_font(draw, "PASSED", WIDTH - 32, start=50, minimum=28)
        _centered(draw, 58, "PASSED", passed_font, "black")
        return image

    number = str(remaining)
    number_font = _fitted_font(draw, number, WIDTH - 32, start=76, minimum=42)
    number_box = draw.textbbox((0, 0), number, font=number_font)
    number_height = number_box[3] - number_box[1]
    number_y = 47 + max(0, (68 - number_height) // 2)
    _centered(draw, number_y, number, number_font, "black")

    label = "DAY LEFT" if remaining == 1 else "DAYS LEFT"
    label_font = _font(17)
    _centered(draw, 126, label, label_font, "black")
    return image


def render_file(config_path: str | Path = "conference.yml", output_path: str | Path | None = None) -> Path:
    conference = load_conference(config_path)
    image = render_conference(conference)
    output = Path(output_path or os.environ.get("PREVIEW_PATH", "/tmp/conference-countdown.png"))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)
    return output


if __name__ == "__main__":
    output = render_file()
    print(f"Rendered {output} ({WIDTH}x{HEIGHT})")
