#!/usr/bin/env python3
"""Open a GitHub issue for each important date that is due a reminder today.

GitHub then notifies the repository owner (email / app, per their notification settings).
Runs daily from .github/workflows/reminders.yml.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import date

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
API = "https://api.github.com/repos/" + REPO


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + TOKEN,
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def add_months(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, d.day)


def next_date(item, today):
    """Next occurrence on or after today. repeat: yearly (default), quarterly or none."""
    parts = [int(x) for x in item["date"].split("-")]
    d = date(*parts) if len(parts) == 3 else date(today.year, parts[0], parts[1])
    repeat = item.get("repeat") or ("none" if item.get("yearly") is False else "yearly")
    step = {"quarterly": 3, "yearly": 12}.get(repeat, 0)
    while step and d < today:
        d = add_months(d, step)
    return d


def main():
    today = date.today()
    items = json.load(open("reminders.json", encoding="utf-8"))
    existing = {i["title"] for i in call("GET", "/issues?state=all&labels=reminder&per_page=100")}
    for item in items:
        when = next_date(item, today)
        days = (when - today).days
        lead = item.get("remind_days", 7)
        if days not in (lead, 0):  # once in advance, and again on the day
            continue
        label = "today" if days == 0 else "tomorrow" if days == 1 else "in %d days" % days
        title = "Reminder: %s %s (%s)" % (item["title"], label, when.strftime("%a %-d %b %Y"))
        if title in existing:
            continue
        call("POST", "/issues", {"title": title, "labels": ["reminder"],
                                 "body": "%s is on %s.\n\nThis reminder was created automatically from `reminders.json`. Close the issue when done." % (item["title"], when.strftime("%A %-d %B %Y"))})
        print("Created:", title)


if __name__ == "__main__":
    main()
