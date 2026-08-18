from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from conference import Conference
from render import HEIGHT, WIDTH, _days_label, _fitted_font, _font, render_conference


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

    def test_secondary_text_uses_gray_while_number_keeps_black(self):
        from datetime import date
        image = render_conference(
            Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
            now=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        colors = {color for _, color in image.getcolors(maxcolors=1_000_000)}
        self.assertIn((0, 0, 0), colors)
        self.assertTrue(any(0 < red < 255 and red == green == blue for red, green, blue in colors))

    def test_days_label_uses_title_case(self):
        self.assertEqual(_days_label(1), "Day Left")
        self.assertEqual(_days_label(2), "Days Left")

    def test_secondary_text_uses_bold_fonts(self):
        from datetime import date

        with patch("render._fitted_font", wraps=_fitted_font) as fitted, patch(
            "render._font", wraps=_font
        ) as font:
            render_conference(
                Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
                now=datetime(2026, 8, 18, tzinfo=timezone.utc),
            )

        self.assertTrue(fitted.call_args_list[0].kwargs.get("bold"))
        self.assertTrue(
            any(call.args == (17,) and call.kwargs.get("bold") for call in font.call_args_list)
        )


if __name__ == "__main__":
    unittest.main()
