"""Small helpers for hand-building Elementor container/widget trees."""

_counter = [0]


def eid():
    _counter[0] += 1
    return f"ug{_counter[0]:05x}"


def px(top, right=None, bottom=None, left=None, unit="px"):
    if right is None:
        right = bottom = left = top
    return {
        "unit": unit, "top": str(top), "right": str(right),
        "bottom": str(bottom), "left": str(left), "isLinked": False,
    }


def size(n, unit="px"):
    return {"unit": unit, "size": n, "sizes": []}


def g(mapping):
    """__globals__ block: {'title_color': 'primary'} -> globals/colors?id=primary"""
    out = {}
    for k, v in mapping.items():
        if v.startswith("typography"):
            out[k] = f"globals/typography?id={v.split(':')[1]}"
        else:
            out[k] = f"globals/colors?id={v}"
    return out


def container(children=None, settings=None, inner=False):
    s = {"content_width": "boxed"}
    s.update(settings or {})
    return {
        "id": eid(), "elType": "container", "settings": s,
        "elements": children or [], "isInner": inner,
    }


def widget(wtype, settings=None):
    return {
        "id": eid(), "elType": "widget", "widgetType": wtype,
        "settings": settings or {}, "elements": [],
    }


# ---------------------------------------------------------------- shorthands

def heading(text, tag="h2", align=None, color_global="secondary",
            typo_global=None, extra=None):
    s = {"title": text, "header_size": tag}
    globals_map = {}
    if color_global:
        globals_map["title_color"] = color_global
    if typo_global:
        globals_map["typography_typography"] = f"typography:{typo_global}"
    if globals_map:
        s["__globals__"] = g(globals_map)
    if align:
        s["align"] = align
    s.update(extra or {})
    return widget("heading", s)


def text(html, align=None, color_global="text", extra=None):
    s = {"editor": html}
    if color_global:
        s["__globals__"] = g({"text_color": color_global})
    if align:
        s["align"] = align
    s.update(extra or {})
    return widget("text-editor", s)


def button(label, link="#", style="solid", align=None, extra=None):
    """style: solid (accent bg) | outline | dark"""
    s = {
        "text": label,
        "link": {"url": link, "is_external": "", "nofollow": "", "custom_attributes": ""},
        "button_type": "",
        "size": "md",
        "border_radius": px(0),
        "text_padding": px(18, 34, 18, 34),
        "typography_typography": "custom",
        "typography_font_weight": "700",
        "typography_text_transform": "uppercase",
        "typography_letter_spacing": size(1.2),
        "typography_font_size": size(14),
    }
    if style == "solid":
        s["__globals__"] = g({"background_color": "accent", "button_text_color": "secondary"})
        s["border_border"] = "solid"
        s["border_width"] = px(2)
        s["__globals__"].update(g({"border_color": "accent"}))
        s["button_background_hover_color"] = "#00000000"
        s["background_hover_color"] = "#00000000"
        s["button_hover_border_color"] = "#00000000"
    elif style == "outline":
        s["background_color"] = "#00000000"
        s["border_border"] = "solid"
        s["border_width"] = px(2)
        s["__globals__"] = g({"button_text_color": "accent", "border_color": "accent"})
    elif style == "dark":
        s["__globals__"] = g({"background_color": "secondary", "button_text_color": "accent"})
        s["border_border"] = "solid"
        s["border_width"] = px(2)
        s["__globals__"].update(g({"border_color": "secondary"}))
    if align:
        s["align"] = align
        s["align_mobile"] = "center"
    s.update(extra or {})
    return widget("button", s)


def image(att_id, url, extra=None):
    s = {"image": {"url": url, "id": att_id, "size": ""}, "image_size": "full"}
    s.update(extra or {})
    return widget("image", s)


def icon_box(icon, title, body, extra=None):
    s = {
        "selected_icon": {"value": icon, "library": "fa-solid"},
        "title_text": title,
        "description_text": body,
        "position": "top",
        "text_align": "left",
        "title_size": "h4",
        "primary_color": "",
        "icon_size": size(44),
        "title_bottom_space": size(12),
        "title_typography_typography": "custom",
        "title_typography_font_size": size(22),
        "title_typography_font_weight": "800",
        "title_typography_text_transform": "uppercase",
        "title_typography_letter_spacing": size(0.5),
        "__globals__": g({
            "primary_color": "secondary",
            "title_color": "secondary",
            "description_color": "text",
        }),
    }
    s.update(extra or {})
    return widget("icon-box", s)


def counter(number, label, suffix="", prefix="+"):
    return widget("counter", {
        "starting_number": 0,
        "ending_number": number,
        "prefix": prefix,
        "suffix": suffix,
        "title": label,
        "thousand_separator": "yes",
        "thousand_separator_char": "'",
        "duration": 1600,
        "typography_number_typography": "custom",
        "typography_number_font_size": size(64),
        "typography_number_font_size_tablet": size(48),
        "typography_number_font_size_mobile": size(40),
        "typography_number_font_weight": "800",
        "typography_title_typography": "custom",
        "typography_title_font_size": size(14),
        "typography_title_font_weight": "700",
        "typography_title_text_transform": "uppercase",
        "typography_title_letter_spacing": size(1.4),
        "__globals__": g({"number_color": "secondary", "title_color": "secondary"}),
    })


def toggle(items):
    """items: list of (title, content)"""
    return widget("toggle", {
        "tabs": [
            {"_id": eid(), "tab_title": t, "tab_content": c} for t, c in items
        ],
        "selected_icon": {"value": "fas fa-chevron-down", "library": "fa-solid"},
        "selected_active_icon": {"value": "fas fa-chevron-up", "library": "fa-solid"},
        "title_html_tag": "div",
        "border_width": size(1),
        "title_padding": px(12, 0, 12, 0),
        "typography_typography": "custom",
        "typography_font_size": size(13),
        "typography_text_transform": "uppercase",
        "typography_letter_spacing": size(1),
        "typography_font_weight": "600",
        "__globals__": g({"title_color": "text", "tab_active_color": "secondary",
                          "content_color": "text", "border_color": "background"}),
    })


def divider_shape(kind="tilt", color_global="accent", where="bottom",
                  height=110, negative=True, flip=False):
    """Angled section divider settings, merged into a container's settings."""
    s = {
        f"shape_divider_{where}": kind,
        f"shape_divider_{where}_height": size(height),
        f"shape_divider_{where}_height_mobile": size(int(height * 0.5)),
    }
    if negative:
        s[f"shape_divider_{where}_negative"] = "yes"
    if flip:
        s[f"shape_divider_{where}_flip"] = "yes"
    s["__globals__"] = g({f"shape_divider_{where}_color": color_global})
    return s


def merge_globals(*dicts):
    """Merge settings dicts, unioning any __globals__ sub-dicts."""
    out, gl = {}, {}
    for d in dicts:
        if not d:
            continue
        d = dict(d)
        gl.update(d.pop("__globals__", {}))
        out.update(d)
    if gl:
        out["__globals__"] = gl
    return out


def row(children, gap=40, align_items=None, settings=None):
    s = {
        "content_width": "full",
        "flex_direction": "row",
        "flex_gap": {"unit": "px", "size": gap, "column": str(gap), "row": str(gap), "isLinked": True},
        "flex_direction_mobile": "column",
        "padding": px(0),
    }
    if align_items:
        s["flex_align_items"] = align_items
    s.update(settings or {})
    return container(children, s, inner=True)


def spans(n, gap, ref=1160):
    """Column width (%) for n columns separated by `gap` px inside `ref` px.

    Elementor's flex gap is added *on top of* the child widths, so plain 100/n
    percentages overflow the row and the last column wraps onto its own line.
    """
    return round((100 - (n - 1) * gap / ref * 100) / n, 2)


def col(children, width=None, width_tablet=100, width_mobile=100, settings=None):
    s = {"content_width": "full", "padding": px(0)}
    if width:
        s["width"] = size(width, "%")
        s["width_tablet"] = size(width_tablet, "%")
        s["width_mobile"] = size(width_mobile, "%")
    s.update(settings or {})
    return container(children, s, inner=True)


def section(children, bg=None, bg_image=None, overlay=None, pad=(110, 20, 110, 20),
            boxed=1200, settings=None, min_height=None):
    s = {
        "content_width": "boxed",
        "boxed_width": size(boxed),
        "padding": px(*pad),
        "padding_tablet": px(int(pad[0] * 0.7), 24, int(pad[2] * 0.7), 24),
        "padding_mobile": px(int(pad[0] * 0.5), 20, int(pad[2] * 0.5), 20),
        "flex_gap": {"unit": "px", "size": 36, "column": "36", "row": "36", "isLinked": True},
    }
    gl = {}
    if bg:
        s["background_background"] = "classic"
        gl["background_color"] = bg
    if bg_image:
        s["background_background"] = "classic"
        s["background_image"] = {"url": bg_image[1], "id": bg_image[0], "size": ""}
        s["background_size"] = "cover"
        s["background_position"] = "center center"
        s["background_repeat"] = "no-repeat"
    if overlay is not None:
        s["background_overlay_background"] = "classic"
        s["background_overlay_color"] = "#0E1216"
        s["background_overlay_opacity"] = size(overlay)
    if min_height:
        s["min_height"] = size(min_height, "vh")
        s["flex_justify_content"] = "center"
    if gl:
        s["__globals__"] = g(gl)
    return container(children, merge_globals(s, settings), inner=False)
