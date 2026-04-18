# Theme Contract

A LumaDeck **theme** is a YAML file in `themes/` that defines a set of
ESPHome `substitutions:`. Themes never define LVGL widgets, fonts, or
hardware. They are pure tokens that layouts and widgets consume.

This document is the **single source of truth** for the substitutions a
theme MUST provide. Any widget or layout in this repo may rely on these
keys existing.

## Naming convention

* All keys are `snake_case`.
* Color values are LVGL hex literals: `"0xRRGGBB"` (quoted strings).
* Numeric values are unitless integers unless otherwise noted.
* Booleans are the strings `"true"` / `"false"` (ESPHome substitutions
  are always strings).

## Required keys

### Colors

| Key            | Purpose                                       |
| -------------- | --------------------------------------------- |
| `bg`           | Primary background                            |
| `bg_alt`       | Secondary surface (cards, panels)             |
| `fg`           | Primary text / icon foreground                |
| `fg_muted`     | Secondary / disabled text                     |
| `accent`       | Brand / interactive accent                    |
| `accent_alt`   | Secondary accent (gradients, highlights)      |
| `success`      | Positive state (on, connected)                |
| `warn`         | Warning state                                 |
| `error`        | Error / offline state                         |
| `border`       | Default border / divider color                |

### Typography

Themes declare **font sizes** as numbers. The actual font ids
(`font_xl`, `font_lg`, `font_md`, `font_sm`, `font_icon`) are produced
by `packages/fonts.yaml` based on these substitutions.

| Key              | Default | Purpose                       |
| ---------------- | ------- | ----------------------------- |
| `font_family`    | `Montserrat` | gfonts family name       |
| `font_size_xl`   | `48`    | Hero clock, big numbers       |
| `font_size_lg`   | `28`    | Section headers               |
| `font_size_md`   | `18`    | Body text                     |
| `font_size_sm`   | `14`    | Captions, secondary labels    |
| `font_size_icon` | `24`    | Icon font glyphs              |

### Shape & spacing

| Key          | Default | Purpose                      |
| ------------ | ------- | ---------------------------- |
| `radius_sm`  | `4`     | Small corner radius          |
| `radius_md`  | `12`    | Default card radius          |
| `radius_lg`  | `24`    | Large surface radius         |
| `radius_pill`| `999`   | Fully-rounded (pills, rings) |
| `pad_sm`     | `4`     | Tight padding                |
| `pad_md`     | `8`     | Default padding              |
| `pad_lg`     | `16`    | Generous padding             |
| `border_w`   | `1`     | Default border width         |

## Optional keys

| Key            | Purpose                                       |
| -------------- | --------------------------------------------- |
| `gradient_a`   | First stop of accent gradient (default = accent)     |
| `gradient_b`   | Second stop of accent gradient (default = accent_alt)|
| `shadow_color` | Shadow tint (default = `0x000000`)            |
| `shadow_op`    | Shadow opacity 0-255 (default = `64`)         |
| `anim_time`    | Default animation duration in ms (default = `200`)   |

## Validation

`tools/validate.py` checks every theme against this contract. Run:

```bash
python -m lumadeck.cli validate themes/dark.yaml
```

## Adding a new theme

1. Copy `themes/_template.yaml` → `themes/<name>.yaml`.
2. Override any subset of the keys above. Anything you omit falls back
   to the defaults in `themes/_template.yaml`.
3. Run validation.
4. Add an entry to `themes/README.md` (if present) or `docs/screen-sizes.md`.
