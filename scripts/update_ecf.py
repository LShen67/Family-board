#!/usr/bin/env python3
"""Fetch a player's ECF rapid ratings and save the last 3 months to ecf.json."""
import html
import json
import re
import sys
import urllib.request
from datetime import date

CODE = "368328L"
NAME = "Louis Shen"
URL = "https://rating.englishchess.org.uk/players?ECF_code=" + CODE
MONTH = re.compile(r"^[A-Z][a-z]{2} \d{4}$")


def text(cell):
    return html.unescape(re.sub(r"<[^>]+>", "", cell)).replace("\xa0", " ").strip()


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "family-board/1.0"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    history = page.split('id="rating_history"', 1)[1]
    rows = []
    for tr in re.findall(r"(?s)<tr>(.*?)</tr>", history):
        cells = [text(c) for c in re.findall(r"(?s)<td[^>]*>(.*?)</td>", tr)]
        # Columns: Standard, Rapid, Blitz, Month, then online ratings
        if len(cells) >= 4 and MONTH.match(cells[3]) and cells[1]:
            rows.append({"month": cells[3], "rating": cells[1]})
    if not rows:
        sys.exit("No rapid ratings found; the ECF page layout may have changed.")
    out = {"name": NAME, "code": CODE, "updated": date.today().isoformat(), "rapid": rows[:3]}
    with open("ecf.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
