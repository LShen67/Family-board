#!/usr/bin/env python3
"""Check HM Land Registry Price Paid Data for new sales in the watched places.

New sales (not seen before) are added to sales.json with today's date, so the
board can show them for 2 days. Runs daily from .github/workflows/sales.yml.
Contains HM Land Registry data © Crown copyright and database right 2026,
licensed under the Open Government Licence v3.0.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import date, timedelta

ENDPOINT = "https://landregistry.data.gov.uk/landregistry/query"
PREFIX = """PREFIX lrppi: <http://landregistry.data.gov.uk/def/ppi/>
PREFIX lrcommon: <http://landregistry.data.gov.uk/def/common/>
"""
SELECT = """SELECT ?tx ?date ?amount ?paon ?saon ?street ?pc WHERE {
  %s
  ?tx lrppi:propertyAddress ?a ; lrppi:pricePaid ?amount ; lrppi:transactionDate ?date .
  OPTIONAL { ?a lrcommon:paon ?paon } OPTIONAL { ?a lrcommon:saon ?saon }
  OPTIONAL { ?a lrcommon:street ?street } OPTIONAL { ?a lrcommon:postcode ?pc }
} ORDER BY DESC(?date) LIMIT 50"""

# Places to watch. "match" is the part of the query that picks the addresses.
WATCH = [
    {"name": "Maunsel Street, SW1P",
     "match": '?a lrcommon:street "MAUNSEL STREET" ; lrcommon:town "LONDON" .'},
    {"name": "Nottingham One, NG1",
     "match": '?a lrcommon:town "NOTTINGHAM" ; lrcommon:paon ?p . FILTER(CONTAINS(?p, "NOTTINGHAM ONE"))'},
    {"name": "Cross Street, SW13 0PS",
     "match": '?a lrcommon:postcode "SW13 0PS" .'},
]
KEEP_DAYS = 30  # how long to keep found sales in the file


def query(match):
    q = PREFIX + SELECT % match
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": q})
    req = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json",
                                               "User-Agent": "family-board/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        rows = json.load(r)["results"]["bindings"]
    return [{k: v["value"] for k, v in row.items()} for row in rows]


def address(row):
    main = " ".join(p.title() for p in [row.get("paon", ""), row.get("street", "")] if p)
    return (row["saon"].title() + ", " + main) if row.get("saon") else main


def main():
    today = date.today()
    path = "sales.json"
    state = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"seen": [], "updates": []}
    first_run = not state["seen"]
    seen = set(state["seen"])
    updates = [u for u in state["updates"] if date.fromisoformat(u["found"]) >= today - timedelta(days=KEEP_DAYS)]

    for w in WATCH:
        for row in query(w["match"]):
            if row["tx"] in seen:
                continue
            seen.add(row["tx"])
            if first_run:
                continue  # don't announce old sales the first time
            updates.append({"place": w["name"], "address": address(row), "price": int(row["amount"]),
                            "sold": row["date"], "found": today.isoformat()})
            print("New sale:", w["name"], address(row), row["amount"], row["date"])

    state = {"checked": today.isoformat(), "seen": sorted(seen), "updates": updates}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    print("Seen %d sales, %d recent updates" % (len(seen), len(updates)))


if __name__ == "__main__":
    main()
