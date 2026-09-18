#!/usr/bin/env python3
"""Compose a few review sheets from the per-breakpoint screenshots.

Every output is kept under 2000px in both dimensions.
"""
from PIL import Image, ImageDraw, ImageFont
import os

SHOTS = "/var/lib/freelancer/projects/40717325/shots"
OUT = "/var/lib/freelancer/projects/40717325/deliverable/screenshots"
os.makedirs(OUT, exist_ok=True)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (24, 26, 30)
FG = (238, 238, 236)
MUTED = (150, 152, 158)


def load(name):
    p = os.path.join(SHOTS, name)
    return Image.open(p).convert("RGB") if os.path.exists(p) else None


def label(d, xy, txt, size=20, colour=FG, font_path=BOLD):
    d.text(xy, txt, font=ImageFont.truetype(font_path, size), fill=colour)


def strip(files, title, out_name, per_row=3, thumb_w=520, caption=None,
          match="width", thumb_h=760):
    """A grid of viewport screenshots.

    match="width"  — every thumbnail scaled to the same width (section flow).
    match="height" — every thumbnail scaled to the same height, which is what
                     a breakpoint comparison needs: a 390px-wide phone shot and
                     a 1280px desktop shot have wildly different aspect ratios,
                     and matching width leaves most of the sheet empty.
    """
    imgs = [(cap, load(f)) for cap, f in files]
    imgs = [(c, im) for c, im in imgs if im]
    if not imgs:
        return None

    scaled = []
    for cap, im in imgs:
        if match == "height":
            w = round(im.width * thumb_h / im.height)
            scaled.append((cap, im.resize((w, thumb_h), Image.LANCZOS)))
        else:
            h = round(im.height * thumb_w / im.width)
            scaled.append((cap, im.resize((thumb_w, h), Image.LANCZOS)))

    rows = [scaled[i:i + per_row] for i in range(0, len(scaled), per_row)]
    gap, pad, cap_h, head_h = 24, 36, 34, 96
    if match == "height":
        width = pad * 2 + max(
            sum(im.width for _, im in r) + gap * (len(r) - 1) for r in rows)
    else:
        width = pad * 2 + per_row * thumb_w + (per_row - 1) * gap
    height = head_h + pad
    for r in rows:
        height += max(im.height for _, im in r) + cap_h + gap

    sheet = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(sheet)
    label(d, (pad, 30), title, 30)
    if caption:
        label(d, (pad, 66), caption, 17, MUTED, REG)

    y = head_h + pad
    for r in rows:
        x = pad
        for cap, im in r:
            label(d, (x, y), cap, 18, MUTED)
            sheet.paste(im, (x, y + cap_h - 8))
            x += im.width + gap
        y += max(im.height for _, im in r) + cap_h + gap

    # Keep both dimensions comfortably under the 2000px limit.
    if max(sheet.size) > 1900:
        f = 1900 / max(sheet.size)
        sheet = sheet.resize((int(sheet.width * f), int(sheet.height * f)), Image.LANCZOS)

    path = os.path.join(OUT, out_name)
    sheet.save(path, quality=88)
    print(f"{out_name}  {sheet.width}x{sheet.height}")
    return path


strip([("Hero + header", "home-desktop-0.png"),
       ("Feature band", "home-desktop-1.png"),
       ("Split + map", "home-desktop-2.png"),
       ("Card row", "home-desktop-3.png"),
       ("Stats band", "home-desktop-4.png"),
       ("CTA + footer", "home-desktop-5.png")],
      "Homepage — section flow (desktop 1280px)", "01-home-desktop.jpg",
      per_row=3, thumb_w=560,
      caption="Angled dividers between every colour band, as on the reference site.")

strip([("Desktop 1280px", "home-desktop-0.png"),
       ("Tablet 900px", "home-tablet-0.png"),
       ("Mobile 390px", "home-mobile-0.png")],
      "Responsive — same page, three breakpoints", "02-responsive.jpg",
      per_row=3, match="height", thumb_h=820,
      caption="Zero horizontal overflow at every width; menu collapses below tablet.")

strip([("Play (main content)", "play-desktop-0.png"),
       ("Design (service)", "design-desktop-0.png"),
       ("About", "about-desktop-0.png"),
       ("Contact", "contact-desktop-0.png"),
       ("Design — process steps", "design-desktop-1.png"),
       ("Design — logo grid", "design-desktop-3.png")],
      "The other page templates", "03-pages.jpg",
      per_row=3, thumb_w=560,
      caption="All eight pages use the same reusable sections and the same global colours.")

# One screenshot per section, cropped to the section itself — scrolling the page
# in fixed viewport steps straddles the boundaries and mislabels every case.
strip([("1 item", "case-2.png"),
       ("2 items", "case-3.png"),
       ("4 items", "case-4.png"),
       ("5 items", "case-5.png")],
      "Self-arranging rows — no empty slots", "05-flexible-layout.jpg",
      per_row=2, thumb_w=760,
      caption="The same section with different numbers of items. Nothing is configured "
              "per case; remove one and the rest re-centre.")

strip([("Cards + stats", "home-mobile-3.png"),
       ("Contact form", "contact-mobile-1.png"),
       ("Footer", "home-mobile-6.png")],
      "Mobile detail (390px)", "04-mobile.jpg",
      per_row=3, match="height", thumb_h=820)
