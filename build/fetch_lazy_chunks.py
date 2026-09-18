#!/usr/bin/env python3
"""Pull in the JS bundles Elementor loads lazily.

wget only follows what is written in the HTML. Elementor's frontend bundle
requests its per-widget handlers (counter, toggle, text-editor, ...) at runtime
via webpack chunk loading, so a plain mirror is missing them and the interactive
bits — the counters counting up, the Description/Details toggles opening — sit
dead while the page still looks perfect in a screenshot.

Copying the whole assets/js folder would be 63MB for a handful of needed files,
so this loads every page in a real browser, notes what 404s, copies just those
from the WordPress install, and repeats until a pass comes back clean (a chunk
can itself request another chunk).
"""
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

SITE = "/var/lib/freelancer/projects/40717325/site"
PREV = "/var/lib/freelancer/projects/40717325/preview"
PORT = 8411
BASE = f"http://127.0.0.1:{PORT}/"
PAGES = ["", "play/", "design/", "about/", "contact/", "scorecard/",
         "useful/", "disclaimer/"]
VIEWPORTS = [(1280, 800), (390, 780)]


def sweep():
    """Load every page, return the set of paths that 404'd."""
    missing = set()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in VIEWPORTS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            # Do NOT filter on the local origin. Elementor reads its assets base
            # from an inline JSON config, which the preview build rewrites to the
            # published GitHub Pages URL — so lazily-loaded chunks are requested
            # from github.io even while the page itself is served from 127.0.0.1.
            # Filtering by origin here made the sweep report a clean run while
            # four bundles were missing.
            pg.on("response", lambda r: missing.add(urlparse(r.url).path)
                  if r.status == 404 and (
                      "/wp-content/" in r.url or "/wp-includes/" in r.url)
                  else None)
            for s in PAGES:
                pg.goto(BASE + s, wait_until="load", timeout=60000)
                pg.wait_for_timeout(1500)
                # Scroll the whole page: handlers load when a widget enters view.
                pg.evaluate("""() => new Promise(done => {
                    let y = 0;
                    const step = () => {
                        y += window.innerHeight;
                        window.scrollTo(0, y);
                        if (y < document.body.scrollHeight) setTimeout(step, 120);
                        else done();
                    };
                    step();
                })""")
                pg.wait_for_timeout(1200)
            ctx.close()
        b.close()
    # Requests made against the published base carry the repo path prefix;
    # strip it so the result is always relative to the mirror root.
    prefix = "/structure-template-preview/"
    cleaned = set()
    for m in missing:
        if m.startswith(prefix):
            m = "/" + m[len(prefix):]
        m = m.lstrip("/")
        if m:
            cleaned.add(m)
    return cleaned


server = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
    cwd=PREV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    subprocess.run(["sleep", "2"], check=False)
    for attempt in range(1, 7):
        missing = sweep()
        if not missing:
            print(f"pass {attempt}: no missing assets")
            break

        copied, unavailable = 0, []
        for rel in sorted(missing):
            src = os.path.join(SITE, rel)
            if not os.path.isfile(src):
                unavailable.append(rel)
                continue
            dst = os.path.join(PREV, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1

        print(f"pass {attempt}: {len(missing)} missing, copied {copied}")
        for u in unavailable:
            print(f"   not in the WordPress install (PHP-only): {u}")
        if copied == 0:
            break
finally:
    server.terminate()
