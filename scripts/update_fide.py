#!/usr/bin/env python3
"""Fetch a player's FIDE rapid ratings and save the latest months to fide.json."""
import html
import json
import re
import sys
import urllib.request
from datetime import date

FIDE_ID = "343451861"
NAME = "Louis Shen"
URL = "https://ratings.fide.com/profile/" + FIDE_ID
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def text(cell):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cell))).strip()


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "family-board/1.0"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    rows = []
    for tr in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", page):
        cells = [text(c) for c in re.findall(r"(?s)<td[^>]*>(.*?)</td>", tr)]
        # Columns: Period (e.g. 2026-Nov), Std, Std games, Rapid, Rapid games, Blitz, Blitz games
        m = re.match(r"^(\d{4})-([A-Z][a-z]{2})$", cells[0]) if cells else None
        if m and len(cells) >= 4 and cells[3].isdigit():
            rows.append({"month": m.group(2) + " " + m.group(1), "rating": cells[3]})
    if not rows:
        sys.exit("No FIDE rapid ratings found; the page layout may have changed.")
    out = {"name": NAME, "id": FIDE_ID, "updated": date.today().isoformat(), "rapid": rows[:3]}
    with open("fide.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
