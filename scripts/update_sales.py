#!/usr/bin/env python3
"""Check HM Land Registry Price Paid Data for new sales in the watched places.

New sales (not seen before) are added to sales.json with today's date, so the
board can show them for 2 days. Runs daily from .github/workflows/sales.yml.
Contains HM Land Registry data © Crown copyright and database right 2026,
licensed under the Open Government Licence v3.0.
"""
import json
import re
import sys
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
     "match": '?a lrcommon:town "NOTTINGHAM" ; lrcommon:paon ?p . FILTER(CONTAINS(?p, "NOTTINGHAM ONE"))',
     "min_rooms": 4},  # 3-bed flat = about 4+ habitable rooms (bedrooms + living room)
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


EPC_API = "https://api.get-energy-performance-data.communities.gov.uk/api"
EPC_TOKEN = os.environ.get("EPC_API_KEY", "")


def epc_get(path, params):
    url = EPC_API + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + EPC_TOKEN,
                                               "Accept": "application/json",
                                               "User-Agent": "family-board/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def find_key(obj, words):
    """Search nested certificate JSON for the first key containing all the words."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if all(w in k.lower() for w in words) and isinstance(v, (int, float, str)) and str(v).strip():
                return v
        for v in obj.values():
            hit = find_key(v, words)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_key(v, words)
            if hit is not None:
                return hit
    return None


def tokens(text):
    return set(re.findall(r"[a-z]*\d+[a-z]*", (text or "").lower()))


def epc_details(row):
    """Habitable rooms and floor area from the property's latest EPC, or {} if not found."""
    if not EPC_TOKEN or not row.get("pc"):
        return {}
    want = tokens(row.get("saon")) or tokens(row.get("paon"))
    try:
        found = epc_get("/domestic/search", {"postcode": row["pc"]}).get("data") or []
        matches = []
        for c in found:
            addr = " ".join(str(c.get(k) or "") for k in ("addressLine1", "addressLine2", "addressLine3"))
            have = tokens(addr)
            if want and want <= have and (row.get("saon") or addr.strip().lower().startswith(sorted(want)[0])):
                matches.append(c)
        if not matches:
            return {}
        latest = sorted(matches, key=lambda c: c.get("registrationDate") or "")[-1]
        cert = epc_get("/certificate", {"certificate_number": latest["certificateNumber"]}).get("data", {})
    except Exception as e:  # never let EPC problems stop the price check
        print("EPC lookup failed for", address(row), "-", type(e).__name__, getattr(e, "code", ""))
        return {}
    rooms = find_key(cert, ["habitable"])
    area = find_key(cert, ["total", "floor", "area"])
    out = {}
    try:
        out["rooms"] = int(float(rooms))
    except (TypeError, ValueError):
        pass
    try:
        out["area"] = round(float(area))
    except (TypeError, ValueError):
        pass
    return out


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
            info = epc_details(row)
            if w.get("min_rooms") and info.get("rooms", 99) < w["min_rooms"]:
                print("Skipped (too few rooms):", address(row), info)
                continue
            u = {"place": w["name"], "address": address(row), "price": int(row["amount"]),
                 "sold": row["date"], "found": today.isoformat()}
            u.update(info)
            updates.append(u)
            print("New sale:", w["name"], address(row), row["amount"], row["date"])

    state = {"checked": today.isoformat(), "seen": sorted(seen), "updates": updates}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    print("Seen %d sales, %d recent updates" % (len(seen), len(updates)))


def test_epc():
    """Look up the EPC for the most recent sale in each place (no changes saved)."""
    print("Token present:", bool(EPC_TOKEN))
    for w in WATCH:
        for row in query(w["match"])[:3]:
            print(w["name"], "|", address(row), row.get("pc"), "->", epc_details(row))


if __name__ == "__main__":
    if "--test-epc" in sys.argv:
        test_epc()
    else:
        main()
