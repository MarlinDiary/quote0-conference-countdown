from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from conference import Conference, days_left, load_conference


WIDTH = 296
HEIGHT = 152
BOLD_FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
)
REGULAR_FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
)
SECONDARY_GRAY = "#777777"


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in BOLD_FONT_PATHS if bold else REGULAR_FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _fitted_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start: int,
    minimum: int,
    *,
    bold: bool = False,
):
    for size in range(start, minimum - 1, -1):
        font = _font(size, bold=bold)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
    return _font(minimum, bold=bold)


def _centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font,
    fill: str,
    *,
    stroke_width: int = 0,
) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    draw.text(
        ((WIDTH - width) / 2, y - box[1]),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=fill,
    )


def _days_label(remaining: int) -> str:
    return "Day Left" if remaining == 1 else "Days Left"


def render_conference(conference: Conference, *, now=None) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    name_font = _fitted_font(draw, conference.name, WIDTH - 32, start=17, minimum=12, bold=True)
    _centered(draw, 14, conference.name, name_font, SECONDARY_GRAY)

    remaining = days_left(conference, now=now)
    if remaining is None:
        passed_font = _fitted_font(draw, "PASSED", WIDTH - 32, start=50, minimum=28, bold=True)
        _centered(draw, 58, "PASSED", passed_font, "black")
        return image

    number = str(remaining)
    number_font = _fitted_font(draw, number, WIDTH - 32, start=78, minimum=42, bold=True)
    number_box = draw.textbbox((0, 0), number, font=number_font)
    number_height = number_box[3] - number_box[1]
    number_y = 40 + max(0, (76 - number_height) // 2)
    _centered(draw, number_y, number, number_font, "black", stroke_width=1)

    label = _days_label(remaining)
    label_font = _font(17, bold=True)
    _centered(draw, 126, label, label_font, SECONDARY_GRAY)
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
