from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from conference import Conference, days_left, load_conference


class ConferenceTests(unittest.TestCase):
    def test_repository_config_has_only_two_fields(self):
        config = load_conference(Path(__file__).parents[1] / "conference.yml")
        self.assertEqual(config.name, "SANER 2027")
        self.assertEqual(config.deadline.isoformat(), "2026-09-25")

    def test_extra_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conference.yml"
            path.write_text("name: TEST\ndeadline: 2026-09-25\ntrack: Research\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "only name and deadline"):
                load_conference(path)

    def test_days_left_uses_local_date_of_aoe_deadline(self):
        config = load_conference(Path(__file__).parents[1] / "conference.yml")
        now = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(days_left(config, now=now), 1)

    def test_days_left_uses_auckland_calendar_days(self):
        config = load_conference(Path(__file__).parents[1] / "conference.yml")
        now = datetime(2026, 8, 18, 23, 30, tzinfo=ZoneInfo("Pacific/Auckland"))
        self.assertEqual(days_left(config, now=now), 39)

    def test_deadline_day_is_zero_days_left_in_auckland(self):
        config = load_conference(Path(__file__).parents[1] / "conference.yml")
        now = datetime(2026, 9, 26, 8, 0, tzinfo=ZoneInfo("Pacific/Auckland"))
        self.assertEqual(days_left(config, now=now), 0)

    def test_passed_deadline_returns_none(self):
        config = load_conference(Path(__file__).parents[1] / "conference.yml")
        now = datetime(2026, 9, 27, 12, 1, tzinfo=timezone.utc)
        self.assertIsNone(days_left(config, now=now))


if __name__ == "__main__":
    unittest.main()
