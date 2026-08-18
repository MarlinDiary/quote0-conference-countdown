from datetime import datetime, timezone
from pathlib import Path
import unittest

from conference import Conference
from render import (
    FONT_BOLD,
    FONT_REGULAR,
    HEIGHT,
    WIDTH,
    _days_label,
    _font,
    render_conference,
)


class RenderTests(unittest.TestCase):
    def test_native_quote0_dimensions(self):
        from datetime import date
        image = render_conference(
            Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
            now=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(image.size, (WIDTH, HEIGHT))
        self.assertEqual(image.size, (296, 152))

    def test_title_is_directly_on_white_background(self):
        from datetime import date
        image = render_conference(
            Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
            now=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(image.getpixel((10, 8)), (255, 255, 255))

    def test_render_uses_only_black_and_white_pixels(self):
        from datetime import date
        image = render_conference(
            Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
            now=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        colors = {color for _, color in image.getcolors(maxcolors=1_000_000)}
        self.assertEqual(colors, {(0, 0, 0), (255, 255, 255)})

    def test_days_label_uses_title_case(self):
        self.assertEqual(_days_label(1), "Day Left")
        self.assertEqual(_days_label(2), "Days Left")

    def test_uses_same_terminus_family_as_ai_usage_display(self):
        self.assertEqual(Path(FONT_REGULAR).name, "terminus-normal.otb")
        self.assertEqual(Path(FONT_BOLD).name, "terminus-bold.otb")
        self.assertEqual(_font(FONT_REGULAR, 18).getname(), ("Terminus", "Medium"))
        self.assertEqual(_font(FONT_BOLD, 28).getname(), ("Terminus", "Bold"))


if __name__ == "__main__":
    unittest.main()
