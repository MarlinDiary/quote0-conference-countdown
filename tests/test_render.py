from datetime import datetime, timezone
import unittest

from conference import Conference
from render import HEIGHT, WIDTH, render_conference


class RenderTests(unittest.TestCase):
    def test_native_quote0_dimensions(self):
        from datetime import date
        image = render_conference(
            Conference(name="SANER 2027", deadline=date(2026, 9, 25)),
            now=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(image.size, (WIDTH, HEIGHT))
        self.assertEqual(image.size, (296, 152))


if __name__ == "__main__":
    unittest.main()
