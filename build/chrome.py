#!/usr/bin/env python3
"""Build the Elementor JSON for the site header and footer (HFE templates)."""
import json, os
from eb import (px, size, g, container, widget, heading, text, image,
                merge_globals, row, col, section, spans)

BUILD = os.path.dirname(os.path.abspath(__file__))
MEDIA = json.load(open(os.path.join(BUILD, "media.json")))


def M(slug):
    m = MEDIA[slug]
    return m["id"], m["url"]


def nav_menu():
    return widget("navigation-menu", {
        "menu": "main-menu",
        "layout": "horizontal",
        "navmenu_align": "right",
        "resp_align": "right",
        "align_items": "right",
        "padding_horizontal_menu_item": size(14),
        "padding_vertical_menu_item": size(8),
        "pointer": "underline",
        "menu_typography_typography": "custom",
        "menu_typography_font_size": size(15),
        "menu_typography_font_weight": "700",
        "menu_typography_text_transform": "uppercase",
        "menu_typography_letter_spacing": size(1),
        "color_menu_item": "#FFFFFF",
        "color_menu_item_hover": "",
        "color_menu_item_active": "",
        "toggle_color": "#FFFFFF",
        "toggle_hover_color": "#FFFFFF",
        "__globals__": g({"color_menu_item_hover": "accent",
                          "color_menu_item_active": "accent"}),
    })


def lang_switcher():
    return widget("html", {"html": (
        '<nav class="ug-lang" aria-label="Language">'
        '<a href="#" class="is-active">EN</a>'
        '<a href="#">DE</a><a href="#">FR</a><a href="#">IT</a>'
        '</nav>')})


def header():
    aid, url = M("logo-light")
    return [container(
        [row([
            col([image(aid, url, extra={
                "width": size(160), "link_to": "custom",
                "link": {"url": "/", "is_external": "", "nofollow": ""}})],
                width=20, width_tablet=30, width_mobile=55,
                settings={"flex_justify_content": "center"}),
            col([nav_menu()], width=58, width_tablet=40, width_mobile=40,
                settings={"flex_justify_content": "center"}),
            col([lang_switcher()], width=16, width_tablet=26, width_mobile=100,
                settings={"flex_justify_content": "center"}),
        ], gap=24, align_items="center",
            settings={"flex_direction_mobile": "row", "flex_wrap_mobile": "wrap"})],
        merge_globals({
            "content_width": "boxed",
            "boxed_width": size(1280),
            "padding": px(14, 24, 14, 24),
            "background_background": "classic",
            "__globals__": g({"background_color": "secondary"}),
        }))]


def newsletter_form():
    return widget("html", {"html": (
        '<form class="ug-newsletter" onsubmit="return false;">'
        '<label class="screen-reader-text" for="ug-nl">Email address</label>'
        '<input id="ug-nl" type="email" placeholder="Email address" />'
        '<button type="submit">Subscribe</button>'
        '<span class="ug-note">Placeholder only &mdash; not connected to a mailing list.</span>'
        '</form>')})


def quick_links():
    labels = [("Home", "/"), ("Play", "/play/"), ("Design", "/design/"),
              ("Scorecard", "/scorecard/"), ("Useful", "/useful/"),
              ("About", "/about/"), ("Contact", "/contact/"),
              ("Disclaimer", "/disclaimer/")]
    return widget("icon-list", {
        "icon_list": [
            {"_id": f"ql{i}", "text": t,
             "link": {"url": u, "is_external": "", "nofollow": ""},
             "selected_icon": {"value": "", "library": ""}}
            for i, (t, u) in enumerate(labels)
        ],
        "space_between": size(2),
        "icon_typography_typography": "custom",
        "icon_typography_font_size": size(14),
        "icon_typography_text_transform": "uppercase",
        "icon_typography_letter_spacing": size(0.6),
        "text_color": "#C9CDD1",
        "text_color_hover": "",
        "divider": "",
        "__globals__": g({"text_color_hover": "accent"}),
    })


def social():
    return widget("social-icons", {
        "social_icon_list": [
            {"_id": "si1", "social_icon": {"value": "fab fa-instagram", "library": "fa-brands"},
             "link": {"url": "#", "is_external": "on", "nofollow": ""}},
            {"_id": "si2", "social_icon": {"value": "fab fa-facebook-f", "library": "fa-brands"},
             "link": {"url": "#", "is_external": "on", "nofollow": ""}},
            {"_id": "si3", "social_icon": {"value": "fab fa-x-twitter", "library": "fa-brands"},
             "link": {"url": "#", "is_external": "on", "nofollow": ""}},
            {"_id": "si4", "social_icon": {"value": "fab fa-linkedin-in", "library": "fa-brands"},
             "link": {"url": "#", "is_external": "on", "nofollow": ""}},
        ],
        "shape": "square",
        "icon_color": "custom",
        "icon_primary_color": "#00000000",
        "icon_secondary_color": "#FFFFFF",
        "icon_size": size(20),
        "icon_spacing": size(10),
        "align": "left",
    })


FOOT_H = {"typography_typography": "custom", "typography_font_size": size(24),
          "typography_font_weight": "800", "typography_text_transform": "uppercase",
          "typography_letter_spacing": size(0.5)}


def footer():
    aid, url = M("logo-light")
    white = {"text_color": "#C9CDD1"}
    return [
        container(
            [row([
                col([image(aid, url, extra={"width": size(170)}),
                     text("<p><strong>Company name</strong><br>Street 00<br>"
                          "0000 City<br>Country</p>", color_global="", extra=white),
                     text('<p><a href="#">+00 00 000 00 00</a><br>'
                          '<a href="#">hello@example.com</a></p>',
                          color_global="", extra=white)], width=30, width_tablet=45),
                col([heading("Newsletter", tag="h3", color_global="",
                             extra=dict(FOOT_H, title_color="#FFFFFF")),
                     text("<p>Sign up with your email address to receive news and "
                          "updates.</p>", color_global="", extra=white),
                     newsletter_form()], width=38, width_tablet=45),
                col([social(),
                     heading("Quick links", tag="h3", color_global="",
                             extra=dict(FOOT_H, title_color="#FFFFFF",
                                        typography_font_size=size(16))),
                     quick_links()], width=22, width_tablet=100),
            ], gap=40, align_items="flex-start", settings={"flex_wrap": "wrap"})],
            merge_globals({
                "content_width": "boxed",
                "boxed_width": size(1280),
                "padding": px(110, 24, 60, 24),
                "padding_mobile": px(70, 20, 40, 20),
                "background_background": "classic",
                "__globals__": g({"background_color": "secondary"}),
            }, {"shape_divider_top": "tilt",
                "shape_divider_top_height": size(100),
                "shape_divider_top_height_mobile": size(50),
                "shape_divider_top_negative": "yes",
                "shape_divider_top_flip": "yes",
                "__globals__": g({"shape_divider_top_color": "background"})})),
        container(
            [row([
                col([text("<p>&copy; 2026 Your company. All rights reserved.</p>",
                          color_global="", extra={"text_color": "#8A9096"})], width=48),
                col([text("<p style='text-align:right'>Legal notice &middot; "
                          "Privacy &middot; Imprint</p>",
                          color_global="", extra={"text_color": "#8A9096"})], width=48),
            ], gap=20, align_items="center")],
            merge_globals({
                "content_width": "boxed",
                "boxed_width": size(1280),
                "padding": px(18, 24, 26, 24),
                "background_background": "classic",
                "__globals__": g({"background_color": "secondary"}),
                "border_border": "solid",
                "border_width": px(1, 0, 0, 0),
                "border_color": "#3A4048",
            })),
    ]


if __name__ == "__main__":
    out = {"header": header(), "footer": footer()}
    path = os.path.join(BUILD, "chrome_data.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("wrote", path, os.path.getsize(path), "bytes")
