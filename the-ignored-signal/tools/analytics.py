#!/usr/bin/env python3
"""
Pull YouTube analytics for the Sub Radar channel — retention, traffic sources,
per-video performance, and a drop-off curve for the top video.

Adds the read-only Analytics scope to the existing upload token. If the current
token lacks it, the first run re-opens the browser (Firefox) for a one-time
consent and upgrades the token in place (upload still works afterward).

Usage:
  python tools/analytics.py                       # last 28 days
  python tools/analytics.py --start 2026-08-01 --end 2026-08-22
  python tools/analytics.py --days 7
"""
import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path

TOOLS         = Path(__file__).resolve().parent
CLIENT_SECRET = TOOLS / "client_secret.json"
TOKEN         = TOOLS / ".youtube_token.json"
# Superset: keep upload/thumbnail so the same token still uploads; add analytics.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

os.environ.setdefault("BROWSER", "firefox")   # one-time consent opens in Firefox


def _token_scopes() -> set[str]:
    if TOKEN.exists():
        return set(json.loads(TOKEN.read_text()).get("scopes") or [])
    return set()


def get_creds():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    have_all = set(SCOPES).issubset(_token_scopes())
    if TOKEN.exists() and have_all:
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and have_all:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise SystemExit(f"Missing {CLIENT_SECRET}.")
            print("Re-authorizing to add the analytics scope "
                  "(a browser window will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json())
    return creds


def _fmt(v, n=1):
    try:
        return f"{float(v):.{n}f}"
    except (TypeError, ValueError):
        return str(v)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sub Radar YouTube analytics report.")
    ap.add_argument("--start", help="YYYY-MM-DD")
    ap.add_argument("--end", help="YYYY-MM-DD")
    ap.add_argument("--days", type=int, default=28, help="window if --start omitted")
    args = ap.parse_args()

    end   = args.end or date.today().isoformat()
    start = args.start or (date.today() - timedelta(days=args.days)).isoformat()

    from googleapiclient.discovery import build
    creds = get_creds()
    yt = build("youtube", "v3", credentials=creds)
    ya = build("youtubeAnalytics", "v2", credentials=creds)

    print(f"\n=== Sub Radar analytics · {start} → {end} ===\n")

    # 1 — channel summary
    s = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics=("views,estimatedMinutesWatched,averageViewDuration,"
                 "averageViewPercentage,subscribersGained,likes,comments,shares"),
    ).execute()
    if s.get("rows"):
        cols = [c["name"] for c in s["columnHeaders"]]
        row  = s["rows"][0]
        print("CHANNEL TOTALS")
        for c, v in zip(cols, row):
            print(f"  {c:26} {v}")
    else:
        print("CHANNEL TOTALS: no data yet (analytics lags ~2–3 days).")
    print()

    # 2 — traffic sources
    ts = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics="views", dimensions="insightTrafficSourceType", sort="-views",
    ).execute()
    print("TRAFFIC SOURCES")
    total = sum(int(r[1]) for r in ts.get("rows", [])) or 1
    for src, views in ts.get("rows", []):
        print(f"  {src:24} {views:>4}  ({100*int(views)/total:.0f}%)")
    if not ts.get("rows"):
        print("  (no data yet)")
    print()

    # 3 — per-video performance (retention is averageViewPercentage)
    pv = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics="views,averageViewPercentage,averageViewDuration,estimatedMinutesWatched",
        dimensions="video", sort="-views", maxResults=25,
    ).execute()
    rows = pv.get("rows", [])
    titles = {}
    if rows:
        ids = [r[0] for r in rows]
        for v in yt.videos().list(part="snippet", id=",".join(ids)).execute()["items"]:
            titles[v["id"]] = v["snippet"]["title"]
    print("PER-VIDEO  (retention% = avg % of video watched)")
    print(f"  {'views':>5} {'ret%':>6} {'avgSec':>7}  title")
    for vid, views, ret, avgdur, _mins in rows:
        print(f"  {views:>5} {_fmt(ret):>6} {_fmt(avgdur):>7}  {titles.get(vid, vid)[:44]!r}")
    if not rows:
        print("  (no data yet)")
    print()

    # 3b — geography (top countries by views)
    geo = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics="views,averageViewPercentage", dimensions="country",
        sort="-views", maxResults=15,
    ).execute()
    grows = geo.get("rows", [])
    print("GEOGRAPHY  (top countries)")
    gtotal = sum(int(r[1]) for r in grows) or 1
    print(f"  {'ctry':>4} {'views':>6} {'share':>6} {'ret%':>6}")
    for country, views, ret in grows:
        print(f"  {country:>4} {views:>6} {100*int(views)/gtotal:>5.0f}% {_fmt(ret):>6}")
    if not grows:
        print("  (no data yet)")
    print()

    # 3c — audience demographics (age group × gender, % of watch time)
    dem = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics="viewerPercentage", dimensions="ageGroup,gender",
        sort="-viewerPercentage",
    ).execute()
    drows = dem.get("rows", [])
    print("VIEWER AGE × GENDER  (% of watch time)")
    if drows:
        # aggregate by age bracket too
        by_age: dict[str, float] = {}
        for age, gender, pct in drows:
            by_age[age] = by_age.get(age, 0.0) + float(pct)
        print("  by age bracket:")
        for age in sorted(by_age):
            label = age.replace("age", "")
            bar = "█" * int(by_age[age] / 2)
            print(f"    {label:>7}  {bar} {by_age[age]:.1f}%")
        print("  age × gender:")
        for age, gender, pct in drows:
            if float(pct) >= 1.0:
                print(f"    {age.replace('age',''):>7} {gender:<6} {float(pct):5.1f}%")
    else:
        print("  (no data yet)")
    print()

    # 4 — drop-off curve for the top video
    if rows:
        top_id = rows[0][0]
        try:
            rc = ya.reports().query(
                ids="channel==MINE", startDate=start, endDate=end,
                metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio",
                filters=f"video=={top_id}",
            ).execute()
            curve = rc.get("rows", [])
            if curve:
                print(f"RETENTION CURVE · top video {titles.get(top_id, top_id)[:40]!r}")
                print("  (elapsed% → % of viewers still watching)")
                for pct, ratio in curve:
                    if abs(float(pct) * 100 % 10) < 1.0:   # every ~10%
                        bar = "█" * int(float(ratio) * 30)
                        print(f"   {float(pct)*100:5.0f}%  {bar} {float(ratio)*100:.0f}%")
        except Exception as e:
            print(f"RETENTION CURVE: unavailable ({str(e)[:80]})")

    print("\nNote: the AI 'Altered content' disclosure is not exposed by any API.")


if __name__ == "__main__":
    main()
