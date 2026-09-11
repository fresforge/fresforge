#!/usr/bin/env python3
"""Generate the animated FR identity panel used by the profile README."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fr-terminal.svg"

ASCII_FR = [
    "███████╗ ██████╗ ",
    "██╔════╝ ██╔══██╗",
    "█████╗   ██████╔╝",
    "██╔══╝   ██╔══██╗",
    "██║      ██║  ██║",
    "╚═╝      ╚═╝  ╚═╝",
]

DETAILS = [
    ("user", "Antonio Andrés"),
    ("role", "Computer Engineering student"),
    ("focus", "Software · Backend · Cloud"),
    ("languages", "TypeScript · Java · Python · C · SQL"),
    ("web", "React · TanStack"),
    ("data", "PostgreSQL · Supabase"),
    ("learning", "Docker · AWS · CI/CD"),
    ("based", "Murcia, Spain"),
]


def render() -> str:
    rows = []
    for index, line in enumerate(ASCII_FR):
        delay = 0.12 + index * 0.10
        rows.append(
            f'<text class="ascii reveal" x="52" y="{112 + index * 34}" '
            f'style="animation-delay:{delay:.2f}s">{escape(line)}</text>'
        )

    details = []
    for index, (key, value) in enumerate(DETAILS):
        delay = 0.55 + index * 0.11
        y = 102 + index * 28
        details.append(
            f'<g class="reveal" style="animation-delay:{delay:.2f}s">'
            f'<text class="key" x="470" y="{y}">{escape(key)}</text>'
            f'<text class="value" x="568" y="{y}">{escape(value)}</text>'
            '</g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="350" viewBox="0 0 860 350" role="img" aria-labelledby="title desc">
  <title id="title">FR — fresforge terminal identity</title>
  <desc id="desc">Antonio Andrés, a Computer Engineering student focused on software engineering, backend systems and cloud.</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="1" stop-color="#0a1320"/>
    </linearGradient>
    <linearGradient id="fr" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#58a6ff"/>
      <stop offset="0.55" stop-color="#2dd4bf"/>
      <stop offset="1" stop-color="#67e8f9"/>
    </linearGradient>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
    .reveal {{ opacity: 0; transform: translateY(7px); animation: reveal .42s cubic-bezier(.2,.8,.2,1) forwards; }}
    .ascii {{ font-size: 26px; font-weight: 700; fill: url(#fr); letter-spacing: .25px; }}
    .key {{ fill: #58a6ff; font-size: 13px; }}
    .value {{ fill: #e6edf3; font-size: 13px; }}
    .cursor {{ animation: blink 1s steps(1,end) infinite; }}
    @keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes blink {{ 0%,48% {{ opacity: 1; }} 49%,100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .reveal {{ opacity: 1; transform: none; animation: none; }} .cursor {{ animation: none; }} }}
  </style>
  <rect width="860" height="350" rx="14" fill="url(#panel)"/>
  <rect x="0.75" y="0.75" width="858.5" height="348.5" rx="13.25" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <line x1="0" y1="42" x2="860" y2="42" stroke="#30363d"/>
  <circle cx="22" cy="21" r="5" fill="#ff5f56"/><circle cx="40" cy="21" r="5" fill="#ffbd2e"/><circle cx="58" cy="21" r="5" fill="#27c93f"/>
  <text x="430" y="26" fill="#7d8590" font-size="12" text-anchor="middle">fresforge@github: ~/identity</text>
  <g filter="url(#softGlow)">{''.join(rows)}</g>
  <text x="54" y="302" fill="#7d8590" font-size="12">FR / FRESFORGE</text>
  <line x1="430" y1="72" x2="430" y2="292" stroke="#21262d"/>
  {''.join(details)}
  <text x="470" y="318" fill="#7d8590" font-size="12">$ build --useful --reliable</text>
  <rect class="cursor" x="702" y="307" width="8" height="14" rx="1" fill="#2dd4bf"/>
</svg>'''


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT}")
