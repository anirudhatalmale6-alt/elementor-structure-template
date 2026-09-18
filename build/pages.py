#!/usr/bin/env python3
"""Build the Elementor page/section JSON for the structural template."""
import json, os
from eb import (eid, px, size, g, container, widget, heading, text, button, image,
                icon_box, counter, toggle, divider_shape, merge_globals, row, col,
                section, spans)

BUILD = os.path.dirname(os.path.abspath(__file__))
MEDIA = json.load(open(os.path.join(BUILD, "media.json")))


def M(slug):
    # The importer renames any attachment whose slug collides with a page slug
    # (scorecard.jpg vs the Scorecard page), so accept either spelling.
    m = MEDIA.get(slug) or MEDIA[slug + "-image"]
    return m["id"], m["url"]


LOREM_SHORT = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
               "Sed do eiusmod tempor incididunt ut labore.")
LOREM = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
         "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
         "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
# Column widths that leave room for the flex gap (see eb.spans).
S2 = spans(2, 60)      # two columns, 60px gap
S3 = spans(3, 36)      # three columns, 36px gap
S4 = spans(4, 30)      # four columns, 30px gap
S2T = spans(2, 36, 760)  # two-up on tablet

LOREM_LONG = (f"<p>{LOREM}</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse "
              "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non "
              "proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"
              f"<p>{LOREM}</p>")


# --------------------------------------------------------------- reusable bits

def hero(title, sub, img_slug, primary="Primary action", secondary="Secondary action",
         tag="h1", min_height=88, divider_to="accent"):
    aid, url = M(img_slug)
    return section(
        [col([
            heading(title, tag=tag, color_global="",
                    extra={"title_color": "#FFFFFF",
                           "typography_typography": "custom",
                           "typography_font_size": size(76),
                           "typography_font_size_tablet": size(52),
                           "typography_font_size_mobile": size(36),
                           "typography_line_height": size(0.95, "em"),
                           "typography_font_weight": "800",
                           "typography_text_transform": "uppercase"}),
            text(f"<p>{sub}</p>", color_global="",
                 extra={"text_color": "#FFFFFF",
                        "typography_typography": "custom",
                        "typography_font_size": size(20),
                        "typography_font_size_mobile": size(16),
                        "typography_font_weight": "500"}),
            row([button(primary, style="solid"),
                 button(secondary, style="outline")],
                gap=18, settings={"flex_wrap": "wrap", "width": size(100, "%")}),
        ], width=70)],
        bg_image=(aid, url), overlay=0.45, pad=(150, 20, 190, 20),
        min_height=min_height,
        settings=divider_shape("tilt", divider_to, "bottom", 120),
    )


def cta_strip(title="Ready to talk about your project?",
              body="Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod.",
              label="Get in touch", link="/contact/"):
    return section(
        [row([
            col([
                heading(title, tag="h2",
                        extra={"typography_typography": "custom",
                               "typography_font_size": size(44),
                               "typography_font_size_mobile": size(28),
                               "typography_font_weight": "800",
                               "typography_line_height": size(1.05, "em"),
                               "typography_text_transform": "uppercase"}),
                text(f"<p>{body}</p>"),
            ], width=56),
            col([button(label, link=link, style="dark", align="left")],
                width=38, settings={"flex_justify_content": "center"}),
        ], gap=48, align_items="center")],
        bg="background", pad=(90, 20, 90, 20),
    )


def stats_band():
    return section(
        [heading("Key numbers", tag="h2",
                 extra={"typography_typography": "custom",
                        "typography_font_size": size(48),
                        "typography_font_size_mobile": size(30),
                        "typography_font_weight": "800",
                        "typography_text_transform": "uppercase"}),
         row([col([counter(1234, "Placeholder metric one")], width=S4, width_tablet=S2T),
              col([counter(56, "Placeholder metric two")], width=S4, width_tablet=S2T),
              col([counter(78, "Placeholder metric three")], width=S4, width_tablet=S2T),
              col([counter(9, "Placeholder metric four")], width=S4, width_tablet=S2T)],
             gap=30, settings={"flex_wrap": "wrap",
                               "flex_justify_content": "center"})],
        bg="accent", pad=(140, 20, 140, 20),
        settings=merge_globals(
            divider_shape("tilt", "background", "top", 110, flip=True),
            divider_shape("tilt", "background", "bottom", 110),
        ),
    )


def card(img_slug, title, with_toggles=True):
    aid, url = M(img_slug)
    kids = [image(aid, url), heading(title, tag="h3",
                                     extra={"typography_typography": "custom",
                                            "typography_font_size": size(26),
                                            "typography_font_weight": "800",
                                            "typography_text_transform": "uppercase"})]
    if with_toggles:
        kids.append(toggle([("Description", f"<p>{LOREM_SHORT}</p>"),
                            ("Details", "<p>Lorem ipsum: 00 &middot; Dolor sit: 00 &middot; "
                                        "Amet: 00</p>")]))
    else:
        kids.append(text(f"<p>{LOREM_SHORT}</p>"))
    return col(kids, width=S3, width_tablet=S2T, settings={"flex_gap": {"unit": "px", "size": 14,
                                                      "column": "14", "row": "14",
                                                      "isLinked": True}})


def card_row(slugs, titles, with_toggles=True):
    # wrap + centre is what makes the row self-arranging: delete a card and the
    # remainder re-centres instead of leaving a hole on the right. One card sits
    # centred, four become a full row plus one centred underneath, and so on.
    return row([card(s, t, with_toggles) for s, t in zip(slugs, titles)],
               gap=36, align_items="flex-start",
               settings={"flex_wrap": "wrap", "flex_justify_content": "center"})


def split(text_children, media_child, reverse=False, bg=None, pad=(110, 20, 110, 20),
          settings=None):
    left = col(text_children, width=S2)
    right = col([media_child], width=S2)
    kids = [right, left] if reverse else [left, right]
    return section([row(kids, gap=60, align_items="center")], bg=bg, pad=pad,
                   settings=settings)


def intro_band(title, sub, bg="background"):
    return section(
        [col([
            heading(title, tag="h1",
                    extra={"typography_typography": "custom",
                           "typography_font_size": size(58),
                           "typography_font_size_tablet": size(44),
                           "typography_font_size_mobile": size(32),
                           "typography_font_weight": "800",
                           "typography_line_height": size(1.0, "em"),
                           "typography_text_transform": "uppercase"}),
            text(f"<p>{sub}</p>", extra={"typography_typography": "custom",
                                         "typography_font_size": size(19),
                                         "typography_font_weight": "500"}),
        ], width=72)],
        bg=bg, pad=(120, 20, 120, 20),
    )


def three_features(items, bg="accent", with_button=True, title=None, sub=None):
    kids = []
    if title:
        kids.append(heading(title, tag="h2",
                            extra={"typography_typography": "custom",
                                   "typography_font_size": size(48),
                                   "typography_font_size_mobile": size(30),
                                   "typography_font_weight": "800",
                                   "typography_line_height": size(1.02, "em"),
                                   "typography_text_transform": "uppercase"}))
    if sub:
        kids.append(col([text(f"<p>{sub}</p>")], width=S2))
    kids.append(row([col([icon_box(i, t, b)], width=spans(3, 40), width_tablet=S2T)
                     for i, t, b in items],
                    gap=40, align_items="flex-start",
                    settings={"flex_wrap": "wrap", "flex_justify_content": "center"}))
    if with_button:
        kids.append(col([button("Learn more", style="dark")], width=100,
                        settings={"flex_align_items": "center"}))
    return section(kids, bg=bg, pad=(140, 20, 140, 20),
                   settings=merge_globals(
                       divider_shape("tilt", "background", "top", 110, flip=True),
                       divider_shape("tilt", "background", "bottom", 110)))


def gmap():
    return widget("google_maps", {
        "address": "Switzerland",
        "zoom": size(7),
        "height": size(520),
        "height_mobile": size(320),
    })


def partner_grid():
    imgs = [image(*M(f"partner-{i:02d}")) for i in range(1, 13)]
    cells = [col([im], width=spans(6, 20), width_tablet=spans(3, 20, 760),
                 settings={"padding": px(18),
                                           "background_background": "classic",
                                           "background_color": "#FFFFFF"})
             for im in imgs]
    return section(
        [heading("They trust us", tag="h2",
                 extra={"typography_typography": "custom",
                        "typography_font_size": size(44),
                        "typography_font_size_mobile": size(28),
                        "typography_font_weight": "800",
                        "typography_text_transform": "uppercase"}),
         col([text(f"<p>{LOREM_SHORT}</p>")], width=S2),
         row(cells, gap=20, align_items="stretch",
             settings={"flex_wrap": "wrap", "flex_justify_content": "center"})],
        bg="background", pad=(110, 20, 110, 20))


# ------------------------------------------------------------------- the pages

def page_home():
    return [
        hero("Your headline<br>goes here.",
             "One supporting sentence describing what you do, in one or two lines.",
             "hero-home", "Primary action", "Secondary action"),
        three_features(
            [("fas fa-bullseye", "Benefit one", LOREM_SHORT),
             ("fas fa-map", "Benefit two", LOREM_SHORT),
             ("fas fa-flag", "Benefit three", LOREM_SHORT)],
            title="Section headline in two lines", sub=LOREM_SHORT),
        split(
            [heading("Split section headline", tag="h2",
                     extra={"typography_typography": "custom",
                            "typography_font_size": size(48),
                            "typography_font_size_mobile": size(30),
                            "typography_font_weight": "800",
                            "typography_line_height": size(1.02, "em"),
                            "typography_text_transform": "uppercase"}),
             text(f"<p>{LOREM}</p>"),
             button("View all", style="solid", align="left")],
            gmap(), bg="background"),
        section([card_row(["card-1", "card-2", "card-3"],
                          ["Item one", "Item two", "Item three"])],
                bg="background", pad=(10, 20, 120, 20)),
        stats_band(),
        cta_strip(),
    ]


def page_play():
    return [
        intro_band("Main content page headline",
                   "Intro paragraph for this section of the site. "
                   "Replace with your own copy later."),
        section([
            heading("Find what you are looking for", tag="h2",
                    extra={"typography_typography": "custom",
                           "typography_font_size": size(48),
                           "typography_font_size_mobile": size(30),
                           "typography_font_weight": "800",
                           "typography_text_transform": "uppercase"}),
            col([text(f"<p>{LOREM_SHORT}</p>")], width=56),
            gmap(),
        ], bg="accent", pad=(140, 20, 140, 20),
            settings=merge_globals(
                divider_shape("tilt", "background", "top", 110, flip=True),
                divider_shape("tilt", "background", "bottom", 110))),
        section([
            heading("All items", tag="h2",
                    extra={"typography_typography": "custom",
                           "typography_font_size": size(44),
                           "typography_font_size_mobile": size(28),
                           "typography_font_weight": "800",
                           "typography_text_transform": "uppercase"}),
            card_row(["card-1", "card-2", "card-3"], ["Item one", "Item two", "Item three"]),
            card_row(["card-4", "card-5", "card-6"], ["Item four", "Item five", "Item six"]),
        ], bg="background", pad=(110, 20, 120, 20)),
        cta_strip(),
    ]


def page_design():
    return [
        hero("Service page headline",
             "One supporting sentence for this service page.",
             "hero-design", "Primary action", "Secondary action", min_height=62),
        section([
            heading("How it works", tag="h2", align="center",
                    extra={"typography_typography": "custom",
                           "typography_font_size": size(48),
                           "typography_font_size_mobile": size(30),
                           "typography_font_weight": "800",
                           "typography_text_transform": "uppercase"}),
            row([col([image(*M(f"step-{i}")),
                      heading(f"0{i} &middot; Step title", tag="h3",
                              extra={"typography_typography": "custom",
                                     "typography_font_size": size(22),
                                     "typography_font_weight": "800",
                                     "typography_text_transform": "uppercase"}),
                      text(f"<p>{LOREM_SHORT}</p>")], width=S3, width_tablet=S2T)
                 for i in (1, 2, 3)],
                gap=36, align_items="flex-start",
                settings={"flex_wrap": "wrap", "flex_justify_content": "center"}),
        ], bg="accent", pad=(140, 20, 140, 20),
            settings=merge_globals(
                divider_shape("tilt", "background", "top", 110, flip=True),
                divider_shape("tilt", "background", "bottom", 110))),
        split([heading("Feature block one", tag="h2",
                       extra={"typography_typography": "custom",
                              "typography_font_size": size(42),
                              "typography_font_size_mobile": size(28),
                              "typography_font_weight": "800",
                              "typography_text_transform": "uppercase"}),
               text(LOREM_LONG),
               button("Read more", style="solid", align="left")],
              image(*M("card-4")), bg="background"),
        split([heading("Feature block two", tag="h2",
                       extra={"typography_typography": "custom",
                              "typography_font_size": size(42),
                              "typography_font_size_mobile": size(28),
                              "typography_font_weight": "800",
                              "typography_text_transform": "uppercase"}),
               text(LOREM_LONG),
               button("Read more", style="solid", align="left")],
              image(*M("card-5")), reverse=True, bg="background",
              pad=(0, 20, 110, 20)),
        partner_grid(),
        cta_strip(),
    ]


def page_about():
    grid = row([col([image(*M(f"grid-{i}"))], width=spans(3, 14, 540),
                    width_tablet=spans(3, 14, 380)) for i in range(1, 10)],
               gap=14, align_items="stretch",
               settings={"flex_wrap": "wrap", "flex_justify_content": "center"})
    return [
        section([row([
            col([heading("About headline in<br>two lines.", tag="h1",
                         extra={"typography_typography": "custom",
                                "typography_font_size": size(52),
                                "typography_font_size_mobile": size(32),
                                "typography_font_weight": "800",
                                "typography_line_height": size(1.02, "em"),
                                "typography_text_transform": "uppercase"}),
                 text(LOREM_LONG)], width=S2),
            col([grid], width=S2),
        ], gap=56, align_items="flex-start")], bg="background", pad=(120, 20, 110, 20)),
        three_features(
            [("fas fa-star", "Value one", LOREM_SHORT),
             ("fas fa-users", "Value two", LOREM_SHORT),
             ("fas fa-leaf", "Value three", LOREM_SHORT)],
            title="What we stand for", with_button=False),
        section([col([
            heading("&ldquo;A pull quote or short statement sits here, "
                    "across two lines.&rdquo;", tag="h2", align="center",
                    color_global="",
                    extra={"title_color": "#FFFFFF",
                           "typography_typography": "custom",
                           "typography_font_size": size(40),
                           "typography_font_size_mobile": size(24),
                           "typography_font_weight": "700",
                           "typography_line_height": size(1.25, "em")}),
            text("<p style='text-align:center'>Name Surname &mdash; Role</p>",
                 color_global="", extra={"text_color": "#FFFFFF"}),
        ], width=80)], bg_image=M("band-wide"), overlay=0.6, pad=(130, 20, 130, 20)),
        cta_strip(),
    ]


def page_contact():
    return [
        section([row([
            col([
                heading("Contact headline", tag="h1",
                        extra={"typography_typography": "custom",
                               "typography_font_size": size(52),
                               "typography_font_size_mobile": size(32),
                               "typography_font_weight": "800",
                               "typography_line_height": size(1.02, "em"),
                               "typography_text_transform": "uppercase"}),
                text(f"<p>{LOREM_SHORT}</p>"),
                widget("shortcode", {"shortcode": "[contact-form-7 id=\"CF7ID\" "
                                                  "title=\"Contact form 1\"]"}),
            ], width=53),
            col([image(*M("contact-side"))], width=42),
        ], gap=56, align_items="flex-start")], bg="background", pad=(110, 20, 100, 20)),
        section([row([
            col([icon_box("fas fa-location-dot", "Address",
                          "Street 00<br>0000 City<br>Country")], width=S3, width_tablet=S2T),
            col([icon_box("fas fa-phone", "Phone",
                          "+00 00 000 00 00<br>Placeholder contact line")], width=S3, width_tablet=S2T),
            col([icon_box("fas fa-clock", "Opening hours",
                          "Mon &ndash; Fri, 00:00 &ndash; 00:00")], width=S3, width_tablet=S2T),
        ], gap=40, align_items="flex-start",
             settings={"flex_wrap": "wrap", "flex_justify_content": "center"})],
            bg="accent", pad=(120, 20, 120, 20),
            settings=merge_globals(
                divider_shape("tilt", "background", "top", 110, flip=True),
                divider_shape("tilt", "background", "bottom", 0, negative=False))),
    ]


def page_simple(title, sub, img_slug=None):
    kids = [intro_band(title, sub)]
    body = [text(LOREM_LONG),
            text(LOREM_LONG)]
    if img_slug:
        kids.append(section([row([col(body, width=53),
                                  col([image(*M(img_slug))], width=42)],
                                 gap=48, align_items="flex-start")],
                            bg="background", pad=(0, 20, 110, 20)))
    else:
        kids.append(section([col(body, width=78)], bg="background", pad=(0, 20, 110, 20)))
    kids.append(cta_strip())
    return kids



def page_layout_demo():
    """Shows the self-arranging row with 1, 2, 4 and 5 items.

    Built so the client can see the behaviour rather than take my word for it:
    the same row settings produce a centred single card, a centred pair, and a
    full row plus a centred remainder — no empty slots left behind.
    """
    slugs = ["card-1", "card-2", "card-3", "card-4", "card-5"]
    titles = ["Item one", "Item two", "Item three", "Item four", "Item five"]

    out = [intro_band("Flexible layout",
                      "The same section with different numbers of items. "
                      "Nothing is configured per case — the row arranges itself.")]
    for n in (1, 2, 4, 5):
        out.append(section(
            [heading(f"{n} item" + ("s" if n > 1 else ""), tag="h2",
                     extra={"typography_typography": "custom",
                            "typography_font_size": size(32),
                            "typography_font_weight": "800",
                            "typography_text_transform": "uppercase"}),
             card_row(slugs[:n], titles[:n], with_toggles=False)],
            bg="background" if n % 2 else "accent",
            pad=(70, 20, 70, 20)))
    return out


PAGES = {
    "home": ("Home", page_home),
    "layout-demo": ("Flexible layout demo", page_layout_demo),
    "play": ("Play", page_play),
    "design": ("Design", page_design),
    "about": ("About", page_about),
    "contact": ("Contact", page_contact),
    "scorecard": ("Scorecard", lambda: page_simple(
        "Secondary page headline",
        "Short intro line for a simple inner page.", "scorecard")),
    "useful": ("Useful", lambda: page_simple(
        "Useful information",
        "Short intro line for a simple inner page.")),
    "disclaimer": ("Disclaimer", lambda: page_simple(
        "Disclaimer",
        "Legal / disclaimer placeholder page.")),
}

# Reusable saved sections offered in the Elementor template library.
SECTIONS = {
    "sec-hero": ("Section - Hero with angled divider",
                 lambda: [hero("Your headline<br>goes here.",
                               "One supporting sentence.", "hero-home")]),
    "sec-cta": ("Section - Call to action strip", lambda: [cta_strip()]),
    "sec-stats": ("Section - Stats band", lambda: [stats_band()]),
    "sec-cards": ("Section - Three cards", lambda: [section(
        [card_row(["card-1", "card-2", "card-3"],
                  ["Item one", "Item two", "Item three"])],
        bg="background", pad=(90, 20, 90, 20))]),
    "sec-features": ("Section - Three icon features", lambda: [three_features(
        [("fas fa-bullseye", "Benefit one", LOREM_SHORT),
         ("fas fa-map", "Benefit two", LOREM_SHORT),
         ("fas fa-flag", "Benefit three", LOREM_SHORT)],
        title="Section headline")]),
    "sec-split": ("Section - Split text / media", lambda: [split(
        [heading("Split section headline", tag="h2",
                 extra={"typography_typography": "custom",
                        "typography_font_size": size(44),
                        "typography_font_weight": "800",
                        "typography_text_transform": "uppercase"}),
         text(f"<p>{LOREM}</p>"), button("Read more", style="solid", align="left")],
        image(*M("card-4")), bg="background")]),
    "sec-partners": ("Section - Logo grid", lambda: [partner_grid()]),
    "sec-intro": ("Section - Page intro band", lambda: [intro_band(
        "Page headline", "Short intro line.")]),
}


if __name__ == "__main__":
    out = {"pages": {}, "sections": {}}
    for slug, (title, fn) in PAGES.items():
        out["pages"][slug] = {"title": title, "data": fn()}
    for slug, (title, fn) in SECTIONS.items():
        out["sections"][slug] = {"title": title, "data": fn()}
    path = os.path.join(BUILD, "elementor_data.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("wrote", path, os.path.getsize(path), "bytes")
