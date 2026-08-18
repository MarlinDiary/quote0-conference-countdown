from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


AOE = timezone(-timedelta(hours=12), name="AoE")
DISPLAY_TIMEZONE = ZoneInfo("Pacific/Auckland")
ALLOWED_KEYS = {"name", "deadline"}


@dataclass(frozen=True)
class Conference:
    name: str
    deadline: date

    @property
    def deadline_at(self) -> datetime:
        """End of the configured date in Anywhere on Earth (UTC-12)."""
        return datetime.combine(self.deadline, time.max, tzinfo=AOE)


def load_conference(path: str | Path = "conference.yml") -> Conference:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("conference.yml must contain a mapping")

    keys = set(data)
    if keys != ALLOWED_KEYS:
        missing = sorted(ALLOWED_KEYS - keys)
        extra = sorted(keys - ALLOWED_KEYS)
        raise ValueError(f"conference.yml must contain only name and deadline; missing={missing}, extra={extra}")

    name = data["name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    name = name.strip()
    if len(name) > 48:
        raise ValueError("name must be at most 48 characters")

    raw_deadline = data["deadline"]
    if isinstance(raw_deadline, datetime):
        raise ValueError("deadline must be a date in YYYY-MM-DD form")
    if isinstance(raw_deadline, date):
        deadline = raw_deadline
    elif isinstance(raw_deadline, str):
        try:
            deadline = date.fromisoformat(raw_deadline)
        except ValueError as exc:
            raise ValueError("deadline must use YYYY-MM-DD") from exc
    else:
        raise ValueError("deadline must use YYYY-MM-DD")

    return Conference(name=name, deadline=deadline)


def days_left(conference: Conference, now: datetime | None = None) -> int | None:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    if now > conference.deadline_at:
        return None

    local_today = now.astimezone(DISPLAY_TIMEZONE).date()
    local_deadline = conference.deadline_at.astimezone(DISPLAY_TIMEZONE).date()
    return (local_deadline - local_today).days
