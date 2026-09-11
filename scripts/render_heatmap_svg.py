#!/usr/bin/env python3
"""Render the fetched contribution data as a self-contained animated SVG."""

from __future__ import annotations

import datetime as dt
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IN_FILE = ROOT / "data" / "contributions.json"
OUT_FILE = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0c2d48", "#0b4f6c", "#087ea4", "#2dd4bf"]
CELL, GAP, STEP = 11, 3, 14
PAD, LABEL_W, TOP_H, BAR_H = 22, 28, 22, 42


def fallback_level(count: int) -> int:
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def build_grid(days: list[dict[str, object]]) -> list[list[dict[str, object] | None]]:
    first = dt.date.fromisoformat(str(days[0]["date"]))
    column: list[dict[str, object] | None] = [None] * ((first.weekday() + 1) % 7)
    grid: list[list[dict[str, object] | None]] = []
    for day in days:
        weekday = (dt.date.fromisoformat(str(day["date"])).weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        column.append(day)
        if len(column) == 7:
            grid.append(column)
            column = []
    if column:
        grid.append(column + [None] * (7 - len(column)))
    return grid


def render(data: dict[str, object]) -> str:
    days = data["days"]
    if not isinstance(days, list) or not days:
        raise ValueError("contribution data contains no days")
    grid = build_grid(days)
    width = 860
    grid_left = PAD + LABEL_W
    grid_top = BAR_H + TOP_H
    available = width - grid_left - PAD
    visible_columns = min(len(grid), available // STEP)
    grid = grid[-visible_columns:]
    height = 252

    month_labels: list[tuple[int, str]] = []
    seen: set[tuple[int, int]] = set()
    for col_index, column in enumerate(grid):
        dated = next((item for item in column if item), None)
        if not dated:
            continue
        date = dt.date.fromisoformat(str(dated["date"]))
        key = (date.year, date.month)
        if key not in seen and date.day <= 7:
            seen.add(key)
            month_labels.append((col_index, date.strftime("%b")))

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">fresforge contribution activity</title>
  <desc id="desc">Public GitHub contribution calendar for the last twelve months, refreshed daily.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0d1117"/><stop offset="1" stop-color="#0a1320"/></linearGradient></defs>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
    .cell {{ opacity: 0; transform: translateY(-5px); animation: cell .34s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes cell {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .cell {{ opacity: 1; transform: none; animation: none; }} }}
  </style>
  <rect width="{width}" height="{height}" rx="14" fill="url(#bg)"/>
  <rect x=".75" y=".75" width="858.5" height="250.5" rx="13.25" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <line x1="0" y1="{BAR_H}" x2="{width}" y2="{BAR_H}" stroke="#30363d"/>
  <circle cx="22" cy="21" r="5" fill="#ff5f56"/><circle cx="40" cy="21" r="5" fill="#ffbd2e"/><circle cx="58" cy="21" r="5" fill="#27c93f"/>
  <text x="430" y="26" fill="#7d8590" font-size="12" text-anchor="middle">fresforge@github: ~/contributions --graph</text>''']

    for col_index, label in month_labels:
        parts.append(f'<text x="{grid_left + col_index * STEP}" y="58" fill="#7d8590" font-size="10">{label}</text>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{PAD}" y="{grid_top + row * STEP + 9}" fill="#7d8590" font-size="9">{name}</text>')

    for col_index, column in enumerate(grid):
        for row_index, day in enumerate(column):
            if day is None:
                continue
            count = int(day["count"])
            level = int(day.get("level", fallback_level(count)))
            level = max(0, min(level, len(PALETTE) - 1))
            x, y = grid_left + col_index * STEP, grid_top + row_index * STEP
            delay = col_index * 0.014 + row_index * 0.025
            plural = "" if count == 1 else "s"
            title = escape(f'{day["date"]}: {count} contribution{plural}')
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.2" '
                f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{title}</title></rect>'
            )

    stats_y = 194
    total = int(data["total_contributions"])
    current = int(data["current_streak"])
    longest = int(data["longest_streak"])
    best = data["best_day"]
    date_range = data["range"]
    parts.extend([
        f'<line x1="22" y1="{stats_y - 18}" x2="838" y2="{stats_y - 18}" stroke="#21262d"/>',
        f'<text x="22" y="{stats_y}" fill="#e6edf3" font-size="13"><tspan fill="#2dd4bf" font-weight="700">{total:,}</tspan><tspan fill="#7d8590"> public contributions · last 12 months</tspan></text>',
        f'<text x="838" y="{stats_y}" fill="#7d8590" font-size="11" text-anchor="end">{date_range["start"]} → {date_range["end"]}</text>',
        f'<text x="22" y="222" fill="#7d8590" font-size="12">current streak <tspan fill="#58a6ff" font-weight="700">{current}d</tspan>   ·   longest <tspan fill="#58a6ff" font-weight="700">{longest}d</tspan></text>',
        f'<text x="838" y="222" fill="#7d8590" font-size="11" text-anchor="end">best day <tspan fill="#e6edf3" font-weight="700">{int(best["count"])}</tspan> · {best["date"]}</text>',
        '</svg>',
    ])
    return "".join(parts)


if __name__ == "__main__":
    payload = json.loads(IN_FILE.read_text(encoding="utf-8"))
    OUT_FILE.write_text(render(payload), encoding="utf-8")
    print(f"wrote {OUT_FILE}")
