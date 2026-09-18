# Structural Website Template — WordPress + Elementor

A clean WordPress foundation whose page structure and section flow follow
[urbangolf.ch](https://www.urbangolf.ch/), built entirely with Elementor
containers and driven by **Elementor Global Colors**.

Everything in it is placeholder content: Lorem Ipsum text, labelled grey image
placeholders, and a neutral colour palette. Nothing is copied from the reference
site — no copy, no images, no branding. Only the *layout skeleton* is replicated,
which is what the brief asks for.

---

## What is in the box

```
theme/structure-child/        Hello Elementor child theme
elementor-templates/          Importable Elementor JSON (pages, sections, header, footer)
build/                        The generator that produced the layouts
screenshots/                  Every page at desktop / tablet / mobile
```

### Pages

| Page         | Slug          | What it demonstrates |
|--------------|---------------|----------------------|
| Home         | `/`           | Hero, 3-up feature band, split text/map, card row, stats band, CTA |
| Play         | `/play/`      | Main content page: intro band, map band, 6-card listing, CTA |
| Design       | `/design/`    | Service page: hero, 3-step process, alternating feature rows, logo grid, CTA |
| About        | `/about/`     | Long text + 3×3 media grid, values band, full-width quote, CTA |
| Contact      | `/contact/`   | Contact form + side image, three info cards |
| Scorecard    | `/scorecard/` | Simple inner page (text + image) |
| Useful       | `/useful/`    | Simple inner page (text only) |
| Disclaimer   | `/disclaimer/`| Simple inner page (text only) |

### Reusable sections

Saved in **Elementor → Templates → Saved Templates**, so you can drop any of them
into a new page from the template library:

`Hero with angled divider` · `Call to action strip` · `Stats band` ·
`Three cards` · `Three icon features` · `Split text / media` · `Logo grid` ·
`Page intro band`

### Header and footer

Built as Elementor templates via the **Header Footer Elementor** plugin (free), so
they are edited visually like any page — no theme file editing. The header carries
the logo, the main menu and a 4-language switcher; the footer carries the logo and
address block, a newsletter signup placeholder, social icons, quick links and a
copyright bar.

---

## The colour palette

**No colour is hard-coded in the layouts.** Every heading, button, background,
divider and icon references an Elementor Global Color. Swapping the palette is a
single screen:

> Elementor → Site Settings (hamburger menu) → **Global Colors**

| Role       | Placeholder | Used for |
|------------|-------------|----------|
| Primary    | `#3A5A78`   | links, accents in body copy |
| Secondary  | `#1F2933`   | header/footer background, headings, dark buttons |
| Text       | `#2B2B2B`   | body copy |
| Accent     | `#E8B54D`   | highlight bands, primary buttons, angled dividers |
| Background | `#F5F4F0`   | page background, light sections |

Replace those five HEX codes with yours, click Update, and the whole site follows.
There is nothing else to change.

Typography works the same way through **Global Fonts**: headings use *Archivo*
(800 weight, uppercase), body text uses *Inter*. Change them in one place.

---

## Installing it

### Option A — import the templates into an existing WordPress

1. Install and activate: **Hello Elementor** theme, **Elementor**,
   **Header Footer Elementor**, **Contact Form 7**.
2. Upload `theme/structure-child` to `wp-content/themes/` and activate
   *Structure Template (Hello Elementor Child)*.
3. **Elementor → Templates → Saved Templates → Import Templates** and upload the
   files from `elementor-templates/`. The `page-*.json` files import as pages, the
   `section-*.json` as reusable sections.
4. For the header and footer, create two templates under **Appearance → Header
   Footer Builder**, set *Type of Template* to Header / Footer and *Display On* to
   Entire Website, then import `site-header.json` / `site-footer.json` into each.
5. Set the palette under Site Settings → Global Colors (values in
   `elementor-templates/global-styles.json`).

### Option B — I install it on your hosting

Send WordPress admin plus FTP or cPanel access and I will do all of the above,
including the menu, the front page setting and the permalinks.

---

## Responsive behaviour

Built mobile-first with three breakpoints (desktop, tablet ≤1024px, mobile ≤767px):

- Multi-column rows go 3-up on desktop, 2-up on tablet, stacked on mobile.
- Headline sizes step down per breakpoint (e.g. hero 76 → 52 → 36px).
- Section padding halves on mobile; angled dividers halve in height.
- The menu collapses to a hamburger below the tablet breakpoint.

Every page was checked at 1280px, 900px and 390px, and verified to have **zero
horizontal overflow** at each. Screenshots of all three are in `screenshots/`.

---

## A note on the angled dividers

The reference site's most recognisable structural trait is that colour bands meet
at a slant rather than a straight edge. That is reproduced with Elementor's own
container shape divider (`tilt`), which means you can change its angle, height,
colour and flip direction from the editor like any other setting.

The child theme force-loads Elementor's `e-shapes` stylesheet. Elementor normally
enqueues it only from the asset list it writes when a document is saved in the
editor; because these layouts are generated, that list can be missing and the
divider SVGs would render unpositioned and overflow the viewport. One line in
`functions.php` removes the dependency on that.

---

## Rebuilding the layouts

The layouts are generated, not hand-drawn, so the source of truth is `build/`:

```
build/eb.py                Elementor container/widget helpers
build/pages.py             the eight page layouts + the reusable sections
build/chrome.py            header and footer
build/import.php           writes everything into WordPress (wp eval-file)
build/export_templates.php writes the importable JSON
build/make_placeholders.py regenerates the placeholder media
build/shoot.py             screenshots every page at three breakpoints
```

Editing a page in Elementor is perfectly fine and is the expected workflow — the
generator only exists so the whole set can be regenerated consistently if the
structure needs to change wholesale.
