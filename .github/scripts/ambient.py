"""Render assets/ambient.svg: tonight's moon over IIT Bhilai, plus a day counter.

Run daily by .github/workflows/ambient.yml. No dependencies beyond the stdlib.
The moon is drawn as a real terminator ellipse, not an emoji, so it matches the
rest of the profile's palette.
"""
from __future__ import annotations

import base64
import datetime as dt
import math
import pathlib

DENIM, BRICK, INK, MUTED = "#6FA8D0", "#B08556", "#DEDAD2", "#8B9099"
BG, LINE = "#0B0D10", "#20252C"

# Akshat's first public push. Used for the "shipping since" counter.
DAY_ZERO = dt.date(2026, 4, 10)
SYNODIC = 29.530588853  # days, mean synodic month
# 2000-01-06 18:14 UTC, a known new moon.
NEW_MOON = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)

NAMES = [
    "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
    "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
]


def phase(now: dt.datetime) -> tuple[float, str]:
    """Return (fraction 0..1 through the cycle, human name)."""
    days = (now - NEW_MOON).total_seconds() / 86400.0
    f = (days % SYNODIC) / SYNODIC
    # Bucket into 8 names, centred so "Full Moon" spans the actual full moon.
    idx = int((f * 8) + 0.5) % 8
    return f, NAMES[idx]


def moon_svg(f: float, cx: float, cy: float, r: float) -> str:
    """Disc plus a terminator ellipse. Lit fraction follows the real phase."""
    # Half-width of the terminator ellipse: +r at new, 0 at quarter, -r at full.
    k = math.cos(2 * math.pi * f)
    rx = abs(k) * r
    waxing = f < 0.5
    # Which side is lit, and whether the terminator is convex or concave.
    lit_right = waxing
    sweep_outer = 1 if lit_right else 0
    sweep_inner = 1 if (k < 0) == lit_right else 0
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#151A20" stroke="{LINE}"/>'
        f'<path d="M {cx} {cy - r} '
        f'A {r} {r} 0 0 {sweep_outer} {cx} {cy + r} '
        f'A {rx:.2f} {r} 0 0 {sweep_inner} {cx} {cy - r} Z" fill="{DENIM}"/>'
    )


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    f, name = phase(now)
    lit = (1 - math.cos(2 * math.pi * f)) / 2 * 100
    days = (now.date() - DAY_ZERO).days

    tile = base64.b64encode(
        (pathlib.Path(__file__).parent / "tile.jpg").read_bytes()
    ).decode()

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="96" viewBox="0 0 760 96" role="img" aria-label="{name}, {lit:.0f} percent lit. Shipping for {days} days.">
  <defs>
    <pattern id="brick" patternUnits="userSpaceOnUse" width="380" height="190">
      <image href="data:image/jpeg;base64,{tile}" width="380" height="190"/>
    </pattern>
  </defs>
  <style>
    .mono {{ font-family:'JetBrains Mono','SFMono-Regular',Consolas,monospace; }}
    .lbl {{ fill:{MUTED}; font-size:10.5px; letter-spacing:.22em; }}
    .val {{ fill:{INK}; font-size:19px; font-weight:700; }}
    .acc {{ fill:{DENIM}; }}
    .wrm {{ fill:{BRICK}; }}
  </style>
  <rect x="0" y="0" width="760" height="96" rx="10" fill="url(#brick)"/>
  <rect x="1" y="1" width="758" height="94" rx="10" fill="{BG}" fill-opacity="0.80" stroke="{LINE}"/>
  {moon_svg(f, 52, 48, 24)}
  <text class="mono lbl" x="98" y="40">TONIGHT OVER IIT BHILAI</text>
  <text class="mono val" x="98" y="66">{name} <tspan class="acc">{lit:.0f}% lit</tspan></text>
  <line x1="430" y1="26" x2="430" y2="70" stroke="{LINE}"/>
  <text class="mono lbl" x="462" y="40">SHIPPING SINCE {DAY_ZERO:%b %Y}</text>
  <text class="mono val" x="462" y="66">{days} <tspan class="wrm">days</tspan></text>
</svg>
'''
    out = pathlib.Path("assets/ambient.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"{name}, {lit:.0f}% lit, day {days}")


if __name__ == "__main__":
    main()
