#!/usr/bin/env python3
"""Collect video links from a Skool community's classroom (all courses/tabs).

Uses your own logged-in browser session (Playwright persistent profile), so no
password is handled by the script. Log in once in the window that opens.

Usage:
    pip install playwright && playwright install chromium
    python scripts/skool_video_links.py my-community-slug
    python scripts/skool_video_links.py my-community-slug --debug   # dumps raw page JSON

Output: skool_<slug>_videos.json and .csv in the current directory.

Note: Skool has no public API. This reads the JSON Skool embeds in each page
(__NEXT_DATA__), with a DOM fallback (iframes / <video>). Field names can change,
so run with --debug if a course comes back empty and adjust VIDEO_KEYS.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://www.skool.com"
VIDEO_KEYS = ("videoLink", "video_link", "videoUrl", "video_url")
MUX_KEYS = ("videoId", "video_id", "playbackId")


def next_data(page):
    raw = page.evaluate(
        "() => document.getElementById('__NEXT_DATA__')?.textContent || null"
    )
    return json.loads(raw) if raw else {}


def walk(node, trail=()):
    """Yield (title_trail, dict) for every dict that carries a video field."""
    if isinstance(node, dict):
        title = node.get("title") or node.get("name")
        meta = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
        merged = {**node, **meta}
        t = trail + ((title,) if isinstance(title, str) else ())
        if any(merged.get(k) for k in VIDEO_KEYS + MUX_KEYS):
            yield t, merged
        for v in node.values():
            yield from walk(v, t)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v, trail)


def plain_text(desc):
    """Skool stores rich text as '[v2]<json>'; flatten it to plain text (best effort)."""
    if not isinstance(desc, str):
        return ""
    if not desc.startswith("[v2]"):
        return desc
    try:
        tree = json.loads(desc[4:])
    except ValueError:
        return desc

    def texts(n):
        if isinstance(n, dict):
            if isinstance(n.get("text"), str):
                yield n["text"]
            for v in n.values():
                if isinstance(v, (list, dict)):
                    yield from texts(v)
            if n.get("type") in ("paragraph", "heading", "listItem"):
                yield "\n"
        elif isinstance(n, list):
            for v in n:
                yield from texts(v)

    return "".join(texts(tree)).strip()


def course_links(page, slug):
    """All /classroom/<id> links, clicking through every tab on the classroom page."""
    pat = re.compile(rf"/{re.escape(slug)}/classroom/([^/?#]+)")
    found = {}

    def grab():
        for href in page.eval_on_selector_all(
            "a[href*='/classroom/']", "els => els.map(e => e.getAttribute('href'))"
        ):
            m = pat.search(href or "")
            if m:
                found[m.group(1)] = f"{BASE}/{slug}/classroom/{m.group(1)}"

    grab()
    for tab in page.query_selector_all("[role=tab]"):
        try:
            tab.click()
            page.wait_for_timeout(800)
            grab()
        except Exception:
            pass
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="community slug, e.g. skool.com/<slug>")
    ap.add_argument("--profile", default=".skool_profile")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    rows, seen = [], set()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(args.profile, headless=False)
        page = ctx.new_page()
        page.goto(f"{BASE}/{args.slug}/classroom")
        input("Log in in the browser window if needed, open the classroom, then press Enter... ")
        page.goto(f"{BASE}/{args.slug}/classroom")
        page.wait_for_load_state("networkidle")

        courses = course_links(page, args.slug)
        print(f"Found {len(courses)} courses", file=sys.stderr)

        for cid, url in courses.items():
            page.goto(url)
            page.wait_for_load_state("networkidle")
            data = next_data(page)
            if args.debug:
                Path(f"debug_{cid}.json").write_text(json.dumps(data, indent=2))
            before = len(rows)
            for trail, d in walk(data):
                link = next((d[k] for k in VIDEO_KEYS if d.get(k)), "")
                mux = next((d[k] for k in MUX_KEYS if d.get(k)), "")
                key = (cid, link or mux)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "course_id": cid,
                        "course_url": url,
                        "lesson": " > ".join(trail[-2:]),
                        "title": d.get("title") or d.get("name") or "",
                        "description": plain_text(d.get("desc") or d.get("description")),
                        "video_link": link,
                        "hosted_video_id": "" if link else mux,
                        "lesson_id": d.get("id", ""),
                    }
                )
            if len(rows) == before:  # DOM fallback for the currently open lesson
                for src in page.eval_on_selector_all(
                    "iframe, video, source", "els => els.map(e => e.src).filter(Boolean)"
                ):
                    rows.append({"course_id": cid, "course_url": url, "lesson": "",
                                 "title": "", "description": "", "video_link": src, "hosted_video_id": "", "lesson_id": ""})
            print(f"  {cid}: {len(rows) - before} videos", file=sys.stderr)
        ctx.close()

    out = Path(f"skool_{args.slug}_videos")
    out.with_suffix(".json").write_text(json.dumps(rows, indent=2))
    with out.with_suffix(".csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["course_id", "course_url", "lesson", "title", "description", "video_link", "hosted_video_id", "lesson_id"]
        )
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}.json / .csv")


if __name__ == "__main__":
    main()
