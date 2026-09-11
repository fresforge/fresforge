#!/usr/bin/env python3
"""Fetch fresforge's public contribution calendar and derive profile stats."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


USERNAME = os.environ.get("GH_PROFILE_USER", "fresforge")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cells: list[dict[str, str]] = []
        self.tooltips: dict[str, str] = {}
        self._tooltip_for: str | None = None
        self._tooltip_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        classes = values.get("class", "").split()
        if tag == "td" and "ContributionCalendar-day" in classes and values.get("data-date"):
            self.cells.append(values)
        elif tag == "tool-tip" and values.get("for"):
            self._tooltip_for = values["for"]
            self._tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self._tooltip_for:
            self._tooltip_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip_for:
            self.tooltips[self._tooltip_for] = " ".join(self._tooltip_text).strip()
            self._tooltip_for = None
            self._tooltip_text = []


def fetch_days() -> list[dict[str, object]]:
    request = urllib.request.Request(URL, headers={"User-Agent": "fresforge-profile-readme/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8")

    parser = ContributionParser()
    parser.feed(source)
    if not parser.cells:
        raise RuntimeError("GitHub contribution cells were not found; its markup may have changed")

    days: list[dict[str, object]] = []
    for cell in parser.cells:
        date = cell.get("data-date")
        if not date:
            continue

        label = parser.tooltips.get(cell.get("id", ""), "")
        match = re.search(r"([\d,]+)\s+contribution", label, re.IGNORECASE)
        count = int(match.group(1).replace(",", "")) if match else 0
        raw_level = cell.get("data-level", "0")
        level = int(raw_level) if str(raw_level).isdigit() else 0
        days.append({"date": date, "count": count, "level": max(0, min(level, 4))})

    if not days:
        raise RuntimeError("GitHub returned a calendar without dated cells")
    return sorted(days, key=lambda day: str(day["date"]))


def streaks(days: list[dict[str, object]]) -> tuple[int, int]:
    counts = [int(day["count"]) for day in days]
    current_index = len(counts) - 1
    if current_index >= 0 and counts[current_index] == 0:
        current_index -= 1

    current = 0
    while current_index >= 0 and counts[current_index] > 0:
        current += 1
        current_index -= 1

    longest = run = 0
    for count in counts:
        run = run + 1 if count > 0 else 0
        longest = max(longest, run)
    return current, longest


def build_payload(days: list[dict[str, object]]) -> dict[str, object]:
    current, longest = streaks(days)
    total = sum(int(day["count"]) for day in days)
    best = max(days, key=lambda day: int(day["count"]))
    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": sum(1 for day in days if int(day["count"]) > 0),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }


if __name__ == "__main__":
    payload = build_payload(fetch_days())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {payload['total_contributions']} public contributions")
