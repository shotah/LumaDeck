# Layout Contract

A LumaDeck **layout** describes a screen *geometry* — its dimensions,
shape, and the named regions where widgets can be anchored. Layouts
never reference specific hardware (no pin numbers, no display drivers).
They expect the consumer device YAML to provide a `display:` and
`touchscreen:` (if any) and only configure LVGL on top.

## Required substitutions a layout MUST declare

| Key             | Example   | Purpose                                  |
| --------------- | --------- | ---------------------------------------- |
| `screen_w`      | `360`     | Display width in px                      |
| `screen_h`      | `360`     | Display height in px                     |
| `screen_shape` | `round`   | `round` \| `square` \| `wide` \| `tall` |
| `screen_radius` | `180`     | For round screens; ignored otherwise     |
| `scale`         | `1.0`     | Informational hint; no math at YAML time (see below) |

### About `scale`

ESPHome's substitution engine is Jinja-based and doesn't support
arbitrary math at config time, so `${scale}` is **not** consumed as
a multiplier (`width: ${100 * scale}` is not valid). It's kept in
the contract as a documentation hint — layouts SHOULD set it
roughly proportional to their physical size, and any widget that
wants per-screen scaling should expose its size as a substitution
the layout can override directly.

## Optional: override widget sizes for the screen

Layouts MAY override widget size and font tokens to fit the
physical screen better. This is the supported way to scale UI per
panel.

```yaml
substitutions:
  # ... required keys above ...

  # Bigger fonts on a small dense AMOLED:
  font_size_md:   "24"
  font_size_lg:   "36"

  # Trim widget heights so they fit the 240 px viewport:
  media_h:        "200"   # default 250
  thermo_h:       "200"   # default 220

  # Shrink wide widgets:
  status_w:       "220"
  nav_w:          "220"
```

The widget contract documents the inline `${var | default(N)}`
pattern that makes these overrides win regardless of include order.
See [`widget-contract.md`](./widget-contract.md#optional-inputs-substitutions-a-widget-may-declare-with-defaults).

## Required pages

Every layout MUST define at least the `home_page` page in its `lvgl:`
block. Optional pages should follow this naming so widgets can target
them consistently:

| Page id        | Purpose                              |
| -------------- | ------------------------------------ |
| `home_page`    | Default landing page                 |
| `media_page`   | Media controls                       |
| `lights_page`  | Light controls                       |
| `climate_page` | Thermostat / climate                 |
| `settings_page`| Brightness, theme, debug             |

## Required regions (anchor ids)

Layouts SHOULD expose invisible `obj` containers as named regions on
`home_page`, so widgets can `align_to:` them rather than guessing
absolute coordinates.

| Region id          | Anchor                          |
| ------------------ | ------------------------------- |
| `region_top`       | Top center (status bar)         |
| `region_center`    | Geometric center (clock)        |
| `region_bottom`    | Bottom center (nav bar)         |
| `region_left`      | Left edge                       |
| `region_right`     | Right edge                      |

A widget that needs custom placement may ignore regions and use its own
coordinates relative to the page.

## Composition pattern (how widgets attach)

Because ESPHome merges packages by id, widgets attach to a layout's
pages by re-declaring the page with `!extend`:

```yaml
lvgl:
  pages:
    - id: !extend home_page
      widgets:
        - label:
            id: lum_clock_lbl
            ...
```

If your ESPHome version doesn't support `!extend` for LVGL pages yet,
include widgets directly inside the layout file (the
`widgets/home_dashboard.yaml` widget shows the composite-widget
fallback pattern).

## Adding a new layout

1. Copy `layouts/_template.yaml` → `layouts/<shape>_<width>.yaml`.
2. Set the substitutions above.
3. Define `home_page` (and any extra pages) with named regions.
4. Add an entry to `docs/screen-sizes.md`.
