# LumaDeck

**A drop-in UI framework for ESPHome + LVGL smart displays.**

Build the UI once — themes, layouts, widgets, icons, swipe nav — then
wire it onto whatever ESP32 panel you've got. LumaDeck stays out of the
way of your hardware.

[![status](https://img.shields.io/badge/status-running%20on%20real%20hardware-22c55e)]()
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![esphome](https://img.shields.io/badge/esphome-2024.6%2B-orange)]()
[![widgets](https://img.shields.io/badge/widgets-16-3b82f6)]()

> **Confirmed running on real hardware.** The
> [LilyGo T-Display-S3 AMOLED](https://lilygo.cc/products/t-display-s3-amoled)
> reference build runs the whole stack — 240×536 AMOLED, CST816 touch,
> swipe-to-page navigation, Material Symbols icons, HA-driven media
> controls. See
> [`examples/lilygo-t-display-amoled.yaml`](./examples/lilygo-t-display-amoled.yaml).

---

## What you get today

| | |
| --- | --- |
| **16 widgets** | clock, analog_clock, status_bar, nav_tabs, media_card, album_art, weather, ring_slider, progress_ring, icon_grid, light_button, scene_button, thermostat, notification_toast, notification_sound, home_dashboard |
| **7 layouts**  | `round_240/360`, `square_240/320`, `tall_240x320`, `tall_240x536`, `wide_480x320`, `wide_536x240` |
| **4 themes**   | `dark`, `light`, `neon`, `high_contrast` (+ `_template`) |
| **Material Symbols icons** | 19 documented codepoints; play/pause and mute auto-swap from HA state |
| **Swipe navigation** | edge-only by default — drag your sliders without cycling pages |
| **Per-screen scaling** | layouts retune widget sizes and font sizes per panel |
| **Home Assistant** | sensor/text_sensor/binary_sensor wired into media, light, weather, thermostat, scene widgets |
| **CLI + Make** | `lumadeck new`, `make verify`, strict CI gate against `esphome config` |
| **Consumer-repo template** | drop-in starter for a hardware repo that pulls LumaDeck as a submodule |

LumaDeck is a **package** — your hardware repo consumes it via
`!include`. It never tells you what panel, driver, or pins to use.

---

## How it composes

Four file types, each with a documented contract:

| Folder      | Job                                              | Contract |
| ----------- | ------------------------------------------------ | -------- |
| `packages/` | Hardware-agnostic ESPHome plumbing (wifi, api, lvgl base, fonts, ha helpers, touch gestures) | n/a |
| `themes/`   | Pure ESPHome `substitutions:` — color + size + radius tokens | [`docs/theme-contract.md`](./docs/theme-contract.md) |
| `layouts/`  | Screen geometry, page skeleton, named regions, per-screen widget overrides | [`docs/layout-contract.md`](./docs/layout-contract.md) |
| `widgets/`  | LVGL components attaching to layout pages via `!extend` | [`docs/widget-contract.md`](./docs/widget-contract.md) |

Swap a theme without touching widgets. Add a widget without touching
layouts. Add a layout without touching widgets. Hardware repos
consume the package without forking it.

See [`docs/architecture.md`](./docs/architecture.md) for the bigger
picture and recommended include order.

---

## Reference hardware

| Panel | Status | Example |
| ----- | ------ | ------- |
| **[LilyGo T-Display-S3 AMOLED](https://lilygo.cc/products/t-display-s3-amoled)** — 1.91", 240×536 AMOLED, RM67162/QSPI, CST816 touch | ✅ flashed + working | [`examples/lilygo-t-display-amoled.yaml`](./examples/lilygo-t-display-amoled.yaml) |
| **[Waveshare ESP32-S3-Touch-LCD-1.85C](https://www.waveshare.com/esp32-s3-touch-lcd-1.85c.htm)** — 360×360 round, ST77916/QSPI, CST816 touch, TCA9554 expander, PCM5101 I²S DAC | ✅ passes `esphome config`, awaiting first-light flash | [`examples/waveshare-1.85c.yaml`](./examples/waveshare-1.85c.yaml) |

Pin maps for the LilyGo are sourced verbatim from the upstream
[LilyGo-AMOLED-Series](https://github.com/Xinyuan-LilyGO/LilyGo-AMOLED-Series)
library. A complete, copy-paste-able **consumer repo template** is in
[`consumer-repo-template/`](./consumer-repo-template/) — that's the
recommended starting point for any new hardware repo.

---

## Quick start

In your hardware repo (next to `secrets.yaml`):

```yaml
substitutions:
  device_name:     "kitchen_panel"
  device_friendly: "Kitchen Panel"

packages:
  core:    !include lumadeck/packages/core.yaml
  board:   !include lumadeck/packages/board_esp32s3.yaml
  theme:   !include lumadeck/themes/dark.yaml
  fonts:   !include lumadeck/packages/fonts.yaml
  display: !include lumadeck/packages/display.yaml
  ha:      !include lumadeck/packages/ha.yaml
  nav:     !include lumadeck/packages/nav.yaml
  touch:   !include lumadeck/packages/touch.yaml
  layout:  !include lumadeck/layouts/wide_536x240.yaml
  status:  !include lumadeck/widgets/status_bar.yaml
  clock:   !include lumadeck/widgets/clock.yaml
  navtabs: !include lumadeck/widgets/nav_tabs.yaml
  media:   !include lumadeck/widgets/media_card.yaml
  toast:   !include lumadeck/widgets/notification_toast.yaml

# add your hardware-specific display: / touchscreen: / lvgl: rotation:
# blocks below — see docs/consumer-repo-guide.md for a working example
```

Full walkthrough:
[`docs/consumer-repo-guide.md`](./docs/consumer-repo-guide.md).

---

## Repo layout

```text
lumadeck/
├── README.md
├── LICENSE                     # MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
├── manifest.yaml               # machine-readable provides/requires
├── pyproject.toml              # `lumadeck` Python CLI
├── Pipfile                     # pipenv mirror of pyproject.toml
├── Makefile                    # `make help` for the catalogue
├── docs/                       # architecture + contracts + authoring guides
├── examples/                   # consumer-style device YAMLs
├── consumer-repo-template/     # drop-in starter for hardware repos
├── packages/                   # core, board_*, fonts, colors, display, ha, nav, touch
├── themes/                     # dark, light, neon, high_contrast, _template
├── layouts/                    # round_*, square_*, wide_*, tall_*, _template
├── widgets/                    # 15 LVGL widgets + _template
├── tools/                      # the `lumadeck` CLI + verify_examples.py
└── tests/                      # pytest suite for the contracts
```

---

## CLI + Make

LumaDeck ships a small Python CLI for scaffolding and validation,
plus a Makefile that wraps everything for one-line commands.

```bash
make install-dev                          # one-time setup (lint/test/validate)
make check                                # lint + validate + test
make new NAME=desk SCREEN=round_360 \
         THEME=dark WIDGETS="clock nav_tabs"

make install-verify                       # one-time, adds ESPHome (~200MB)
make verify                               # `esphome config` every example
```

`make verify` is the strict gate that catches LVGL syntax issues
before they hit hardware. CI runs it on every push. See
[`docs/verifying-examples.md`](./docs/verifying-examples.md) for what
the output should look like.

Direct CLI:

```bash
pip install -e .
lumadeck list themes
lumadeck new desk_panel --screen round_360 --theme dark --widget clock
lumadeck validate-all
pytest
```

Pipenv works too — `Pipfile` mirrors `pyproject.toml`:

```bash
pipenv install --dev
pipenv run check
```

Windows users without `make`: install via `choco install make` /
`scoop install make`, or run the underlying commands directly.

---

## Documentation

| Doc | What's in it |
| --- | ------------ |
| [`docs/architecture.md`](./docs/architecture.md) | How packages / themes / layouts / widgets compose |
| [`docs/theme-contract.md`](./docs/theme-contract.md) | Required substitution keys for any theme |
| [`docs/layout-contract.md`](./docs/layout-contract.md) | Required substitutions, page ids, region anchors |
| [`docs/widget-contract.md`](./docs/widget-contract.md) | Header format, id naming, the inline-default pattern |
| [`docs/authoring-a-theme.md`](./docs/authoring-a-theme.md) | 5-min walkthrough |
| [`docs/authoring-a-layout.md`](./docs/authoring-a-layout.md) | New screen size or shape |
| [`docs/authoring-a-widget.md`](./docs/authoring-a-widget.md) | New UI component |
| [`docs/screen-sizes.md`](./docs/screen-sizes.md) | Matrix of supported geometries |
| [`docs/icons.md`](./docs/icons.md) | Material Symbols catalogue + how to add glyphs |
| [`docs/touch-gestures.md`](./docs/touch-gestures.md) | Edge-swipe wiring + tuning knobs |
| [`docs/verifying-examples.md`](./docs/verifying-examples.md) | `make verify` walkthrough |
| [`docs/consumer-repo-guide.md`](./docs/consumer-repo-guide.md) | How a hardware repo imports LumaDeck |

---

## Roadmap

### v0.1 — shipped ✅

* Hardware-agnostic core + board split (esp32 / s3 / c3)
* Theme contract + 4 themes
* Layout contract + 7 layouts
* Widget contract + 15 widgets
* CLI: `list`, `new`, `validate`, `validate-all`
* `make verify` strict gate against `esphome config`
* Pytest suite + CI (yamllint + validate + test + verify)
* **First confirmed hardware build (LilyGo T-Display-S3 AMOLED)**

### v0.2 — most landed early ✅

* Touch gesture abstraction with **edge-only swipe** to prevent
  slider/arc conflicts
* `album_art` widget pulling HA `entity_picture` via `online_image`
* Material Symbols icon font wired into `nav_tabs`, `media_card`,
  `status_bar`; play/pause + mute icons auto-swap from HA state
* Per-screen scaling (per-widget size overrides + per-layout font sizes)
* Volume slider + mute toggle on `media_card`
* `analog_clock` with rotating hands (`transform_rotation`)
* Animated `notification_toast` slide-in/out

### v0.3 — open

* `lumadeck preview` static screenshot renderer (for docs)
* Widget registry (machine-readable index)
* Live theme reload over the API
* Vertical swipe gestures (pull-to-refresh, dismiss toast)
* `gauge.yaml`, `calendar_agenda.yaml` widgets
* Edge-only-swipe + LVGL widget conflict refinements

### v1.0

* HACS-style installer
* Community widget marketplace
* Semver guarantees on the contracts

See [`todo.md`](./todo.md) for the priority-ordered next-up list and
[`CHANGELOG.md`](./CHANGELOG.md) for what's actually landed.

---

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). The shortest version: copy
the relevant `_template.yaml`, fill it in, run `make check` (and
`make verify` if you touched widgets), open a PR.

---

## Why use it

ESPHome users love hardware but hate writing repetitive UI YAML.
LumaDeck makes the UI side reusable — you wire up GPIO and pin maps
once, then pick widgets like a deck of cards. A new device is a
15-line YAML file plus your driver block.

Because every widget is verified against ESPHome's actual LVGL
schema (`make verify` runs on every push), upgrading LumaDeck won't
silently break your build — schema regressions get caught upstream.

Because the package is hardware-agnostic, the same `media_card.yaml`
that runs on the LilyGo AMOLED today will run on the next ESP32-P4
panel tomorrow, swapping only the driver block in your consumer repo.
