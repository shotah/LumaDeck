# Widget Contract

A LumaDeck **widget** is a YAML file in `widgets/` that adds one or
more LVGL components to a layout's pages. Widgets are the most
numerous file type and the easiest place for the community to
contribute.

## Rules

1. **Read-only on themes.** A widget may reference any substitution
   from `docs/theme-contract.md`. It MUST NOT define new color or
   font-size substitutions of its own (use the theme tokens).
2. **Anchored to layout pages.** A widget targets pages by id
   (`home_page`, `media_page`, etc.). It MUST NOT create top-level
   pages of its own — that's a layout's job.
3. **Namespaced ids.** Every `id:` a widget creates MUST be prefixed
   with `lum_<widget_name>_`. Example: in `widgets/clock.yaml`,
   `lum_clock_lbl`, `lum_clock_ampm`, etc.
4. **No hardware.** No pins, no `i2c:`, no `spi:`, no `display:`.
5. **Idempotent include.** Including the same widget twice should
   produce a clear error or merge cleanly — never silently double up.
6. **Documented inputs/outputs.** The widget header comment MUST list:
   * substitutions it reads
   * page ids it targets
   * ids it exposes to the consumer
   * Home Assistant entities/services it expects (if any)

## Header template

Every widget file MUST start with a comment block like this:

```yaml
# ---------------------------------------------------------------
# widget: <name>
# version: 0.1.0
# reads:        ${bg} ${fg} ${accent} ${font_lg}
# targets:      home_page
# exposes:      lum_<name>_<id> ...
# ha_entities:  <optional>
# ha_services:  <optional>
# ---------------------------------------------------------------
```

## Optional inputs (substitutions a widget may declare with defaults)

A widget MAY accept widget-specific configuration via substitutions
prefixed with the widget name. **Two patterns**, used for different
purposes:

### 1. Inline default — for sizes/positions a layout may override

Use Jinja's `default()` filter directly in the YAML value. This is
the right pattern for anything a layout could reasonably want to
retune per screen (root width/height, key offsets, button sizes).

```yaml
# in widgets/status_bar.yaml — DOES NOT declare status_w in
# its substitutions: block. This way layouts (or device YAMLs) can
# set `status_w: 480` and it wins regardless of include order.
lvgl:
  ...
  width: ${status_w | default(220)}
  height: ${status_h | default(24)}
```

### 2. Substitutions block — for per-instance configuration

Things that are widget-instance config (entity ids, labels, format
strings) belong in the `substitutions:` block. The consumer overrides
them at the device level.

```yaml
# in widgets/clock.yaml
substitutions:
  clock_format:    "%H:%M"
  clock_date_fmt:  "%a %b %d"
  clock_show_date: "true"
```

### Why two patterns?

ESPHome substitutions follow "**later included package wins**". A
widget's `substitutions:` block is a top-level package include, so
its values can beat earlier-included layout overrides. The inline
`default()` pattern sidesteps this entirely — the widget never
"claims" the substitution name, so any prior or later override wins.

**Rule of thumb**: if a layout could plausibly want to set it
differently, use inline `default()`. If it's per-device user
configuration, declare it in `substitutions:`.

## Composing widgets into a "screen"

A composite widget (like `widgets/home_dashboard.yaml`) is allowed and
encouraged for opinionated reference UIs. It still follows every rule
above — it just bundles several smaller widgets' worth of LVGL into
one file.

## Adding a new widget

1. Copy `widgets/_template.yaml` → `widgets/<name>.yaml`.
2. Fill in the header comment.
3. Add the `lvgl:` (and `interval:` / `button:` / `text_sensor:` /
   etc.) blocks needed.
4. Add an example in `examples/` that uses it, and at minimum verify
   `esphome config` succeeds against that example.
5. Optionally add `widgets/<name>.md` documenting the widget in detail.
