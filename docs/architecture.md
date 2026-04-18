# Architecture

LumaDeck is built around four file types that compose cleanly via
ESPHome's `packages:` mechanism. Each has a clear, narrow job.

```
+-------------------+    +----------------+    +-----------------+
|   packages/       |    |   themes/      |    |   layouts/      |
|  (infrastructure) |    |  (design       |    |  (screen        |
|                   |    |   tokens)      |    |   geometry)     |
+---------+---------+    +-------+--------+    +--------+--------+
          \\                     |                       /
           \\                    |                      /
            \\        +----------v-----+               /
             \\       |  device YAML   |              /
              \\------>  (consumer     <-------------/
                      |   repo)       |
                      +-------+-------+
                              |
                              | !include widgets
                              v
                     +-----------------+
                     |   widgets/      |
                     |  (UI components)|
                     +-----------------+
```

## packages/

Hardware-and-render-agnostic ESPHome plumbing.

* `core.yaml` — `esphome:`, `wifi:`, `api:`, `ota:`, `time:`. No board.
* `board_<chip>.yaml` — picks the ESP variant + framework.
* `display.yaml` — base LVGL config + `style_definitions:`.
* `fonts.yaml` — declares the standard font ids based on theme sizes.
* `colors.yaml` — semantic color aliases on top of the theme palette.
* `nav.yaml` — page-navigation `script:` actions.
* `ha.yaml` — Home Assistant service-call wrappers.
* `touch.yaml` — touch input abstractions (no driver).

## themes/

Pure ESPHome `substitutions:`. Define the design tokens the rest of
the system reads. See [`theme-contract.md`](./theme-contract.md) for
the required keys.

## layouts/

Screen geometry. Each layout sets `screen_w`, `screen_h`,
`screen_shape`, and a `scale` factor, then defines an `lvgl:` block
containing at least `home_page` and (optionally) other pages with
named region anchors. See [`layout-contract.md`](./layout-contract.md).

## widgets/

LVGL components that attach themselves to layout pages by id, using
`!extend home_page`. Widgets read theme substitutions, never hardware.
See [`widget-contract.md`](./widget-contract.md).

## tools/

Optional Python CLI (`pip install -e .`) that scaffolds new device
YAMLs and validates files against the contracts.

## Composition order

When ESPHome merges packages, later includes can extend earlier ones.
The recommended include order in a consumer device YAML is:

1. `core` — base ESPHome
2. `board_*` — chip variant
3. `theme/*` — design tokens
4. `fonts` — depends on theme sizes
5. `colors` — depends on theme palette (optional)
6. `display` — depends on theme tokens
7. `ha` / `nav` / `touch` — optional integrations
8. `layout/*` — pages and regions
9. `widgets/*` — final UI

## Why this split?

* Themes can be swapped without touching widgets.
* Widgets can be added without touching layouts.
* Layouts can be added without touching widgets.
* Hardware repos consume the package without forking it.
