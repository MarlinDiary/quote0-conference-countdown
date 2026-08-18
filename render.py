from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from conference import Conference, days_left, load_conference


WIDTH = 296
HEIGHT = 152
BLACK = 0
WHITE = 255

_HERE = Path(__file__).parent
FONT_REGULAR = _HERE / "fonts" / "terminus-normal.otb"
FONT_BOLD = _HERE / "fonts" / "terminus-bold.otb"
BITMAP_FONT_SIZES = (32, 28, 24, 22, 20, 18, 16, 14, 12)


def _font(path: str | Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def _fitted_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start: int,
    minimum: int,
    *,
    path: str | Path = FONT_REGULAR,
) -> ImageFont.FreeTypeFont:
    sizes = [size for size in BITMAP_FONT_SIZES if minimum <= size <= start]
    for size in sizes:
        font = _font(path, size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
    return _font(path, minimum)


def _centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    draw.text(((WIDTH - width) // 2, y - box[1]), text, font=font, fill=BLACK)


def _scaled_bitmap_text(
    text: str,
    *,
    path: str | Path,
    font_size: int,
    max_scale: int,
    max_width: int,
    max_height: int,
    tracking: int = 2,
) -> Image.Image:
    font = _font(path, font_size)
    probe = ImageDraw.Draw(Image.new("1", (1, 1), WHITE))
    advances = [int(probe.textlength(character, font=font)) for character in text]
    base_width = sum(advances) + tracking * max(0, len(text) - 1)
    base = Image.new("1", (base_width, font_size), WHITE)
    draw = ImageDraw.Draw(base)

    x = 0
    for character, advance in zip(text, advances):
        draw.text((x, 0), character, font=font, fill=BLACK)
        x += advance + tracking

    scale = max(1, min(max_scale, max_width // base.width, max_height // base.height))
    return base.resize((base.width * scale, base.height * scale), Image.Resampling.NEAREST)


def _days_label(remaining: int) -> str:
    return "Day Left" if remaining == 1 else "Days Left"


def render_conference(conference: Conference, *, now=None) -> Image.Image:
    image = Image.new("1", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)

    name_font = _fitted_font(draw, conference.name, WIDTH - 32, start=18, minimum=12)
    _centered(draw, 12, conference.name, name_font)

    remaining = days_left(conference, now=now)
    if remaining is None:
        passed = _scaled_bitmap_text(
            "PASSED",
            path=FONT_BOLD,
            font_size=28,
            max_scale=2,
            max_width=WIDTH - 32,
            max_height=76,
        )
        image.paste(passed, ((WIDTH - passed.width) // 2, 50))
        return image.convert("RGB")

    number = _scaled_bitmap_text(
        str(remaining),
        path=FONT_BOLD,
        font_size=28,
        max_scale=3,
        max_width=WIDTH - 32,
        max_height=84,
    )
    image.paste(number, ((WIDTH - number.width) // 2, 36 + (84 - number.height) // 2))

    label_font = _font(FONT_REGULAR, 18)
    _centered(draw, 128, _days_label(remaining), label_font)
    return image.convert("RGB")


def render_file(
    config_path: str | Path = "conference.yml",
    output_path: str | Path | None = None,
) -> Path:
    conference = load_conference(config_path)
    image = render_conference(conference)
    output = Path(output_path or os.environ.get("PREVIEW_PATH", "/tmp/conference-countdown.png"))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)
    return output


if __name__ == "__main__":
    output = render_file()
    print(f"Rendered {output} ({WIDTH}x{HEIGHT})")
