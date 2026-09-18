#!/usr/bin/env python3
"""Strip the cache-busting query string out of mirrored asset filenames.

wget --restrict-file-names=windows saves `style.css?ver=1.0` as
`style.css@ver=1.0`. A static host then has no idea it is CSS: the extension is
`.css@ver=1.0`, so it is served as application/octet-stream and the browser
refuses to apply it under strict MIME checking. The page still returns 200 for
every asset, which is why this shows up as a silent layout collapse rather than
a 404 — the give-away is the page height, not the network tab.

So: rename every `name.ext@anything` to `name.ext`, then rewrite the references
in the HTML and CSS that point at the old names.
"""
import os
import re

ROOT = "/var/lib/freelancer/projects/40717325/preview"
TEXT_EXT = {".html", ".css", ".js", ".xml", ".json", ".svg"}

renames = {}

for dirpath, _dirnames, filenames in os.walk(ROOT):
    for name in filenames:
        if "@" not in name:
            continue
        clean = name.split("@", 1)[0]
        if not clean:
            continue
        src = os.path.join(dirpath, name)
        dst = os.path.join(dirpath, clean)
        if os.path.exists(dst):
            # Same asset already mirrored without a query string — drop the dup.
            os.remove(src)
        else:
            os.rename(src, dst)
        renames[name] = clean

print(f"renamed {len(renames)} asset files")

# Longest first so `a.css@ver=1` is replaced before a shorter prefix could match.
ordered = sorted(renames.items(), key=lambda kv: -len(kv[0]))

touched = 0
for dirpath, _dirnames, filenames in os.walk(ROOT):
    for name in filenames:
        if os.path.splitext(name)[1].lower() not in TEXT_EXT:
            continue
        path = os.path.join(dirpath, name)
        with open(path, encoding="utf-8", errors="replace") as fh:
            body = fh.read()
        before = body
        for old, new in ordered:
            if old in body:
                body = body.replace(old, new)
        # Any surviving ?ver= in a page URL points at a file that does not exist
        # under these flattened names. HTML only: minified JS contains template
        # literals like `...swiper.js?ver=${v}` and an unanchored strip eats the
        # closing backtick, turning a working bundle into a syntax error that no
        # 404 or failed request ever reveals.
        if name.lower().endswith(".html"):
            body = re.sub(r'(\.(?:css|js))\?[^"\'\s)]*', r'\1', body)
        if body != before:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)
            touched += 1

print(f"rewrote references in {touched} files")

stragglers = [
    os.path.join(d, f)
    for d, _s, fs in os.walk(ROOT) for f in fs if "@" in f
]
print(f"files still carrying a query string in the name: {len(stragglers)}")
for s in stragglers[:5]:
    print("  ", s)
