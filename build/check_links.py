#!/usr/bin/env python3
"""Follow every internal link on every page and report where it actually lands.

This exists because of a bug a client found in ten seconds that my own checks
missed completely. I had verified the preview by navigating straight to
/play/, /design/, ... which all returned 200 — but never once clicked the menu.
The mirror's navigation pointed at `index.html@p=47` shortlink copies that the
cleanup step had deleted, so every menu item was dead while every page I tested
was fine.

Verifying a destination is not verifying the link that points at it. This walks
the site the way a visitor does: collect anchors, resolve them, and confirm each
one serves a real page.

Usage: check_links.py <base-url>
"""
import sys
from collections import defaultdict
from urllib.parse import urldefrag, urljoin, urlparse

from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1
        else "https://anirudhatalmale6-alt.github.io/structure-template-preview/")
ROOT = BASE.rstrip("/") + "/"


def internal(url):
    return url.startswith(ROOT)


def main():
    seen, queue = set(), [ROOT]
    broken = defaultdict(list)   # target -> pages that link to it
    placeholders = defaultdict(list)
    ok_pages = []

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 800})

        while queue:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            resp = pg.goto(url, wait_until="domcontentloaded", timeout=90000)
            status = resp.status if resp else 0
            title = (pg.title() or "").strip()

            # A static host answers a missing path with a 404 page that still
            # renders; check the status, not whether something appeared.
            if status >= 400:
                broken["(direct)"].append(f"{status} {url}")
                continue
            ok_pages.append((status, url, title))

            anchors = pg.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.getAttribute('href'))")
            for href in anchors:
                if href is None:
                    continue
                raw = href.strip()
                if raw.startswith(("mailto:", "tel:", "javascript:")):
                    continue
                target, _frag = urldefrag(urljoin(url, raw))
                if raw in ("#", "") or (target.rstrip("/") == url.rstrip("/")
                                        and raw.startswith("#")):
                    placeholders[url].append(raw or "#")
                    continue
                if internal(target) and target not in seen:
                    queue.append(target)

        # Now confirm every discovered internal target resolves.
        for target in sorted(seen):
            resp = pg.goto(target, wait_until="domcontentloaded", timeout=90000)
            if not resp or resp.status >= 400:
                broken[target].append(resp.status if resp else "no response")

        b.close()

    print(f"pages reached by following links: {len(ok_pages)}")
    for status, url, title in sorted(ok_pages, key=lambda r: r[1]):
        print(f"  {status}  {url}   [{title}]")

    dead = {k: v for k, v in broken.items() if v}
    print(f"\nbroken links: {len(dead)}")
    for target, who in dead.items():
        print(f"  DEAD {target}  <- {who}")

    total_ph = sum(len(v) for v in placeholders.values())
    print(f"\nplaceholder anchors (href='#', expected in a template): {total_ph}")

    return 1 if dead else 0


sys.exit(main())
