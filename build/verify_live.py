#!/usr/bin/env python3
"""Confirm the published preview: fonts, language switcher, self-arranging rows."""
from playwright.sync_api import sync_playwright

B = "https://anirudhatalmale6-alt.github.io/structure-template-preview/"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 800})

    for path in ["", "layout-demo/"]:
        r = pg.goto(B + path, wait_until="load", timeout=90000)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(2500)
        h1 = pg.evaluate(
            "getComputedStyle(document.querySelector('h1,h2')).fontFamily").split(",")[0]
        urb = pg.evaluate("document.fonts.check('800 40px Urbanist')")
        rob = pg.evaluate("document.fonts.check('400 17px Roboto')")
        print(f"{path or 'home':13s} {r.status}  heading={h1:12s} "
              f"urbanist_rendered={urb}  roboto_rendered={rob}")

    pg.goto(B, wait_until="load")
    pg.wait_for_timeout(1500)
    print("switcher:", pg.eval_on_selector_all(
        ".ug-lang a", "els => els.map(e => e.textContent.trim())"))

    # Measure the row behaviour rather than eyeballing the screenshot: for each
    # self-arranging row, how many items and how many distinct rows do they
    # occupy, and is the last row centred?
    pg.goto(B + "layout-demo/", wait_until="load")
    pg.wait_for_timeout(2000)
    rows = pg.evaluate("""() => {
        const out = [];
        document.querySelectorAll('.e-con').forEach(r => {
            const cs = getComputedStyle(r);
            if (cs.display !== 'flex' || cs.justifyContent !== 'center') return;
            const kids = Array.from(r.children).filter(k => k.offsetHeight);
            if (kids.length < 1) return;
            const tops = [...new Set(kids.map(k => Math.round(
                k.getBoundingClientRect().top)))];
            const lastTop = Math.max(...tops);
            const lastRow = kids.filter(k => Math.round(
                k.getBoundingClientRect().top) === lastTop);
            const boxes = lastRow.map(k => k.getBoundingClientRect());
            const left = Math.min(...boxes.map(x => x.left));
            const right = Math.max(...boxes.map(x => x.right));
            const parent = r.getBoundingClientRect();
            const gapL = Math.round(left - parent.left);
            const gapR = Math.round(parent.right - right);
            out.push({items: kids.length, lines: tops.length,
                      last_line: lastRow.length,
                      left_gap: gapL, right_gap: gapR,
                      centred: Math.abs(gapL - gapR) <= 2});
        });
        return out;
    }""")
    for r in rows:
        print("  row:", r)

    b.close()
