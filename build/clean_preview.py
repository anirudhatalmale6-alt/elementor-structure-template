#!/usr/bin/env python3
"""Tidy the static mirror before publishing it as a preview.

wget rewrites every asset it actually downloaded to a relative path, but it
leaves two things pointing back at the build machine:

  * WordPress head metadata (feeds, wp-json, xmlrpc, the emoji loader) — dead
    requests in the browser console, so they get stripped outright;
  * absolute URLs inside inline <script> JSON (Elementor's frontend config:
    assets path, uploads path, ajaxurl) — these are escaped as http:\\/\\/...
    so wget never touched them. Elementor's JS reads the assets path at
    runtime, so those are rewritten to the published base URL.

The preview is also marked noindex: a throwaway demo should never show up in
search results.
"""
import glob
import os
import re

ROOT = "/var/lib/freelancer/projects/40717325/preview"
BASE = "https://anirudhatalmale6-alt.github.io/structure-template-preview/"
LOCAL = "http://localhost:8407/"

DROP_PATTERNS = [
    r'<link[^>]*rel=["\'](?:alternate|EditURI|wlwmanifest)["\'][^>]*>',
    r'<link[^>]*rel=["\']https://api\.w\.org/["\'][^>]*>',
    r'<link[^>]*(?:wp-json|xmlrpc\.php|/feed/)[^>]*>',
    r'<script[^>]*>\s*(?:/\*\s*<!\[CDATA\[\s*\*/\s*)?window\._wpemojiSettings.*?</script>',
    r'<script[^>]*wp-emoji-(?:release|loader)[^>]*>\s*</script>',
    r'<script[^>]*src=["\'][^"\']*wp-emoji[^"\']*["\'][^>]*>\s*</script>',
    r'<style[^>]*>\s*img\.wp-smiley.*?</style>',
    # WP 7.x ships the emoji config as a JSON block plus a loader script; the
    # loader then builds a URL to wp-emoji-release.min.js at runtime, which no
    # static host can serve. Drop both.
    r'<script[^>]*id=["\']wp-emoji-settings["\'][^>]*>.*?</script>',
    r'<script[^>]*wp-emoji-loader[^>]*>.*?</script>',
]

NOINDEX = '<meta name="robots" content="noindex, nofollow">'

# WordPress advertises every page twice — the pretty permalink and a ?p=ID
# shortlink — so a crawl can save `index.html@p=47` copies and then rewrite the
# navigation to point at them. Deleting those files (what this used to do) left
# every menu item dead while each page still answered fine on its own URL, which
# is exactly the bug that shipped. The shortlink is now suppressed in the child
# theme and ?p= is rejected during the crawl, so these should never exist; if one
# turns up, stop rather than quietly delete it.
strays = glob.glob(os.path.join(ROOT, "**", "index.html@p=*"), recursive=True)
if strays:
    raise SystemExit(
        "shortlink duplicates present in the mirror — the navigation would point "
        "at them:\n  " + "\n  ".join(strays))

changed = 0
for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    before = html

    for pat in DROP_PATTERNS:
        html = re.sub(pat, "", html, flags=re.I | re.S)

    # The emoji detector is inlined and minified, so `_wpemojiSettings` appears
    # in the middle of the block rather than at the start — a pattern anchored
    # to the opening tag misses it. Drop any script block that mentions it,
    # otherwise removing only its JSON config leaves the loader throwing.
    html = re.sub(
        r'<script\b[^>]*>(?:(?!</script>).)*?wpemoji(?:(?!</script>).)*?</script>',
        "", html, flags=re.I | re.S)

    # Escaped form inside inline JSON, then any plain absolute leftovers.
    html = html.replace(LOCAL.replace("/", r"\/"), BASE.replace("/", r"\/"))
    html = html.replace(LOCAL, BASE)

    # Contact Form 7's script fetches its validation schema from the REST API on
    # load. On a static host that returns the 404 HTML page, which CF7 then tries
    # to parse as JSON — a console error on every visit to the contact page. The
    # form cannot submit here anyway, so drop its scripts and keep the markup.
    html = re.sub(
        r'<script\b[^>]*(?:contact-form-7|/swv/|wpcf7)[^>]*>(?:(?!</script>).)*?</script>',
        "", html, flags=re.I | re.S)
    html = re.sub(
        r'<script\b[^>]*>(?:(?!</script>).)*?wpcf7(?:(?!</script>).)*?</script>',
        "", html, flags=re.I | re.S)

    if NOINDEX not in html:
        html = html.replace("<head>", "<head>\n" + NOINDEX, 1)

    if html != before:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        changed += 1

print(f"cleaned {changed} html files")

leftover = 0
for path in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True):
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            leftover += fh.read().count(b"localhost:8407")
print(f"remaining localhost references: {leftover}")
