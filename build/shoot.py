#!/usr/bin/env python3
"""Screenshot every page of the local build at three breakpoints."""
import os, sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8407"
OUT = "/var/lib/freelancer/projects/40717325/shots"
os.makedirs(OUT, exist_ok=True)

PAGES = ["", "play", "design", "about", "contact", "scorecard"]
VIEWPORTS = {"desktop": (1280, 800), "tablet": (900, 800), "mobile": (390, 780)}

only = sys.argv[1:] or None


def run():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for vp, (w, h) in VIEWPORTS.items():
            if only and vp not in only and not any(o in PAGES for o in only):
                pass
            ctx = b.new_context(viewport={"width": w, "height": h},
                                device_scale_factor=1)
            page = ctx.new_page()
            page.on("pageerror", lambda e: errors.append(f"[{vp}] JS: {e}"))
            page.on("response", lambda r: errors.append(
                f"[{vp}] {r.status} {r.url}") if r.status >= 400 else None)
            for slug in PAGES:
                url = f"{BASE}/{slug}" if slug else BASE + "/"
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(1800)
                total = page.evaluate("document.body.scrollHeight")
                n = min(7, max(1, -(-total // h)))
                name = slug or "home"
                for i in range(n):
                    page.evaluate(f"window.scrollTo(0,{i * h})")
                    page.wait_for_timeout(700)
                    page.screenshot(path=f"{OUT}/{name}-{vp}-{i}.png")
                # horizontal overflow check
                ovf = page.evaluate(
                    "document.documentElement.scrollWidth - "
                    "document.documentElement.clientWidth")
                print(f"{name:10s} {vp:8s} h={total:5d} shots={n} h-overflow={ovf}px")
            ctx.close()
        b.close()
    if errors:
        print("\n--- page errors ---")
        for e in dict.fromkeys(errors):
            print(" ", e)
    else:
        print("\nno JS errors, no 4xx/5xx responses")


run()
