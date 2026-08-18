import unittest
from unittest.mock import patch

import display


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


class DisplayConfigTests(unittest.TestCase):
    def test_remote_config_is_downloaded_and_validated(self):
        with patch.object(display, "CONFIG_URL", "https://example.test/conference.yml"), patch.object(
            display.requests, "get", return_value=FakeResponse("name: SANER 2027\ndeadline: 2026-09-25\n")
        ) as get:
            path = display.current_config_path()
            try:
                self.assertTrue(path.exists())
                self.assertEqual(path.read_text(encoding="utf-8"), "name: SANER 2027\ndeadline: 2026-09-25\n")
                get.assert_called_once_with("https://example.test/conference.yml", timeout=15)
            finally:
                path.unlink(missing_ok=True)

    def test_invalid_remote_config_is_removed(self):
        with patch.object(display, "CONFIG_URL", "https://example.test/conference.yml"), patch.object(
            display.requests, "get", return_value=FakeResponse("name: SANER 2027\n")
        ):
            with self.assertRaises(ValueError):
                display.current_config_path()


if __name__ == "__main__":
    unittest.main()
