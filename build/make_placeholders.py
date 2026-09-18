#!/usr/bin/env python3
"""Generate neutral placeholder media for the structural template."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/var/lib/freelancer/projects/40717325/build/media"
os.makedirs(OUT, exist_ok=True)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def centred(d, box, text, f, fill):
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - w) / 2 - bb[0], y0 + (y1 - y0 - h) / 2 - bb[1]), text, font=f, fill=fill)


def placeholder(name, w, h, label, bg=(214, 212, 206), fg=(122, 120, 114), grid=True):
    """A calm grey placeholder with a cross, a label and its own dimensions."""
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    if grid:
        step = max(40, min(w, h) // 8)
        line = tuple(min(255, c + 10) for c in bg)
        for x in range(0, w, step):
            d.line([(x, 0), (x, h)], fill=line, width=1)
        for y in range(0, h, step):
            d.line([(0, y), (w, y)], fill=line, width=1)
    pad = min(w, h) * 0.12
    d.line([(pad, pad), (w - pad, h - pad)], fill=fg, width=2)
    d.line([(w - pad, pad), (pad, h - pad)], fill=fg, width=2)
    d.rectangle([pad, pad, w - pad, h - pad], outline=fg, width=3)

    size = max(18, min(w, h) // 12)
    f1 = font(BOLD, size)
    f2 = font(REG, max(14, int(size * 0.6)))
    tb = d.textbbox((0, 0), label, font=f1)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    dim = f"{w} x {h}"
    db = d.textbbox((0, 0), dim, font=f2)
    dw, dh = db[2] - db[0], db[3] - db[1]
    block_h = th + dh + size * 0.5
    bx0 = (w - max(tw, dw)) / 2 - size * 0.8
    by0 = (h - block_h) / 2 - size * 0.55
    d.rectangle([bx0, by0, w - bx0, h - by0], fill=bg)
    d.text(((w - tw) / 2 - tb[0], by0 + size * 0.5 - tb[1]), label, font=f1, fill=(70, 68, 64))
    d.text(((w - dw) / 2 - db[0], by0 + size * 0.5 + th + size * 0.45 - db[1]), dim, font=f2, fill=fg)
    img.save(os.path.join(OUT, name), quality=88)
    return name


def logo(name, w, h, dark_text=True):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (43, 43, 43, 255) if dark_text else (245, 244, 240, 255)
    d.rectangle([2, 2, w - 3, h - 3], outline=col, width=3)
    centred(d, (0, 0, w, h), "YOUR LOGO", font(BOLD, int(h * 0.30)), col)
    img.save(os.path.join(OUT, name))
    return name


def partner(name, w, h, i):
    img = Image.new("RGB", (w, h), (245, 244, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, w - 11, h - 11], outline=(198, 196, 190), width=2)
    centred(d, (0, 0, w, h * 0.62), f"LOGO {i:02d}", font(BOLD, int(h * 0.20)), (120, 118, 112))
    centred(d, (0, h * 0.58, w, h), "partner placeholder", font(REG, int(h * 0.10)), (160, 158, 152))
    img.save(os.path.join(OUT, name), quality=88)
    return name


made = []
made.append(placeholder("hero-home.jpg", 1920, 1080, "HERO IMAGE"))
made.append(placeholder("hero-play.jpg", 1920, 900, "HERO IMAGE"))
made.append(placeholder("hero-design.jpg", 1920, 900, "HERO IMAGE"))
made.append(placeholder("hero-about.jpg", 1920, 900, "HERO IMAGE"))
made.append(placeholder("band-wide.jpg", 1920, 800, "FULL WIDTH IMAGE"))
made.append(placeholder("contact-side.jpg", 900, 1200, "SIDE IMAGE"))
for i in (1, 2, 3, 4, 5, 6):
    made.append(placeholder(f"card-{i}.jpg", 800, 600, f"CARD IMAGE {i}"))
for i in range(1, 10):
    made.append(placeholder(f"grid-{i}.jpg", 600, 600, f"GRID {i}"))
made.append(placeholder("step-1.jpg", 800, 800, "STEP 1"))
made.append(placeholder("step-2.jpg", 800, 800, "STEP 2"))
made.append(placeholder("step-3.jpg", 800, 800, "STEP 3"))
made.append(placeholder("map-placeholder.jpg", 1200, 900, "MAP AREA"))
made.append(placeholder("scorecard.jpg", 1200, 800, "SCORECARD IMAGE"))
for i in range(1, 13):
    made.append(partner(f"partner-{i:02d}.png", 300, 200, i))
made.append(logo("logo-dark.png", 260, 90, dark_text=True))
made.append(logo("logo-light.png", 260, 90, dark_text=False))

print(f"{len(made)} files written to {OUT}")
