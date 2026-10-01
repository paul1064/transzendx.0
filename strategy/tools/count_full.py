#!/usr/bin/env python3
"""Count FULL cycles in the last 24h of journal/cycles.log — AGENT-EDITABLE.

Portable replacement for the awk one-liner in schedule.json `notes` (that
one needs GNU `date -d`, which macOS lacks, and loop.sh's tool allowlist
does not permit awk). Same contract as COUNT COMMAND v4: a line counts
only if it starts with "<UTC ISO> cycle done", falls in the last 24h, and
its FIRST tick marker is "(FULL cycle" (a later quoted "(LIGHT tick" or
"(FULL cycle" never flips it). Prints one integer; copy it verbatim.

Usage: python3 strategy/tools/count_full.py [--hours 24]
"""
import argparse
import datetime as dt
import pathlib
import re

LOG = pathlib.Path(__file__).resolve().parents[2] / "journal" / "cycles.log"
LINE = re.compile(r"^20[0-9-]+T[0-9:]+Z cycle done")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=24)
    a = ap.parse_args()
    cut = (dt.datetime.now(dt.timezone.utc)
           - dt.timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M")
    n = 0
    for line in LOG.read_text().splitlines():
        if not LINE.match(line) or line.split()[0][:16] <= cut:
            continue
        i, j = line.find("(FULL cycle"), line.find("(LIGHT tick")
        if i >= 0 and (j < 0 or i < j):
            n += 1
    print(n)


if __name__ == "__main__":
    main()
