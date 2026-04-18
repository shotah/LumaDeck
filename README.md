# LumaDeck

**Universal UI package system for ESPHome + LVGL displays.**

A reusable theme + widget + layout framework for ESP32 smart panels
running ESPHome. Build the UI once, deploy it across round, square,
and rectangular screens — touch or non-touch.

License: [MIT](./LICENSE)

---

## Vision

Build once, deploy everywhere:

* Round screens
* Square screens
* Rectangular / portrait screens
* Touch or non-touch devices
* Media remotes, room controllers, clocks, status panels

LumaDeck is a **package** — your hardware repo consumes it via
`!include`. It never tells you what panel, driver, or pins to use.

## Reference hardware

LumaDeck ships ready-to-flash example device YAMLs for two real
panels:

* **[LilyGo T-Display-S3 AMOLED](https://lilygo.cc/products/t-display-s3-amoled)**
  — 240x536 portrait AMOLED, 1.91", RM67162 over QSPI, optional
  CST816T touch.
  Example: [`examples/lilygo-t-display-amoled.yaml`](./examples/lilygo-t-display-amoled.yaml).
  Pin map sourced from the upstream
  [LilyGo-AMOLED-Series](https://github.com/Xinyuan-LilyGO/LilyGo-AMOLED-Series)
  library.

* **[Waveshare ESP32-S3-Touch-LCD-1.85C](https://www.waveshare.com/esp32-s3-touch-lcd-1.85c.htm)**
  — 360x360 round, capacitive touch.
  Example (driver block stubbed): [`examples/waveshare-1.85c.yaml`](./examples/waveshare-1.85c.yaml).

A complete, copy-paste-able **consumer repo template** is in
[`consumer-repo-template/`](./consumer-repo-template/) — that's the
recommended starting point for any hardware repo.

---

## Repo layout

```text
lumadeck/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── manifest.yaml
├── pyproject.toml
├── docs/                  # architecture + contracts + authoring guides
├── examples/              # consumer-style device YAMLs
├── packages/              # core, board_*, fonts, colors, display, ha, nav, touch
├── themes/                # dark, light, neon, high_contrast, _template
├── layouts/               # round_*, square_*, wide_*, tall_*, _template
├── widgets/               # clock, media_card, weather, ring_slider, ...
├── tools/                 # the `lumadeck` CLI (generate / validate)
└── tests/                 # pytest suite for the contracts
```

## The four file types

| Folder      | Job                                              | Contract |
| ----------- | ------------------------------------------------ | -------- |
| `packages/` | Hardware-agnostic ESPHome plumbing (wifi, api, lvgl base, fonts, ha helpers) | n/a |
| `themes/`   | Pure ESPHome `substitutions:` — color + size tokens | [`docs/theme-contract.md`](./docs/theme-contract.md) |
| `layouts/`  | Screen geometry + page skeleton + named regions  | [`docs/layout-contract.md`](./docs/layout-contract.md) |
| `widgets/`  | LVGL components attaching to layout pages        | [`docs/widget-contract.md`](./docs/widget-contract.md) |

See [`docs/architecture.md`](./docs/architecture.md) for the bigger
picture and recommended include order.

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
  layout:  !include lumadeck/layouts/round_360.yaml
  clock:   !include lumadeck/widgets/clock.yaml
  navtabs: !include lumadeck/widgets/nav_tabs.yaml

# add your hardware-specific display: / touchscreen: blocks below
```

Full walkthrough:
[`docs/consumer-repo-guide.md`](./docs/consumer-repo-guide.md).

---

## CLI (optional)

LumaDeck ships a small Python CLI for scaffolding and validation.

```bash
pip install -e .

lumadeck list themes
lumadeck list layouts
lumadeck list widgets

lumadeck new desk_panel \
    --screen round_360 \
    --theme  dark \
    --widget clock \
    --widget nav_tabs

lumadeck validate themes/dark.yaml
lumadeck validate-all
```

Run the test suite with `pytest`.

### Make targets

A `Makefile` wraps everything above. Run `make help` for the catalogue:

```bash
make install-dev                          # one-time setup (lint/test/validate)
make check                                # lint + validate + test
make new NAME=desk SCREEN=round_360 \
         THEME=dark WIDGETS="clock nav_tabs"

make install-verify                       # one-time, adds ESPHome (~200MB)
make verify                               # `esphome config` every example
```

`make verify` is the recommended way to confirm the LumaDeck YAML
actually compiles against your ESPHome version. See
[`docs/verifying-examples.md`](./docs/verifying-examples.md) for a
walkthrough of the output.

Windows users without `make`: install via `choco install make` /
`scoop install make`, or run the underlying commands directly.

### Pipenv

A `Pipfile` mirrors `pyproject.toml`. If you prefer pipenv:

```bash
pipenv install --dev
pipenv run check
```

---

## Built-in themes, layouts, widgets

**Themes:** `dark`, `light`, `neon`, `high_contrast`
(+ `_template.yaml`)

**Layouts:** `round_240`, `round_360`, `square_240`, `square_320`,
`tall_240x320`, `wide_480x320` (+ `_template.yaml`)

**Widgets:** `clock`, `analog_clock`, `status_bar`, `nav_tabs`,
`media_card`, `album_art`, `weather`, `ring_slider`, `progress_ring`,
`icon_grid`, `light_button`, `scene_button`, `thermostat`,
`notification_toast`, `home_dashboard` (+ `_template.yaml`)

---

## Roadmap

### v0.1 (this release)

* Hardware-agnostic core + board split (esp32 / s3 / c3)
* Theme contract + 4 themes
* 6 layouts covering round/square/wide/tall
* 15 widgets
* CLI: `list`, `new`, `validate`, `validate-all`
* Pytest suite for the contracts

### v0.2

* Touch gesture abstraction (`packages/touch.yaml` + swipe pages)
* Album-art HTTP fetcher
* Brightness ring slider wired to display backlight
* Resolution auto-scaling via `${scale}` everywhere

### v0.3

* `lumadeck preview` LVGL simulator
* Widget registry (machine-readable index)
* Live theme reload over the API

### v1.0

* HACS-style installer
* Community widget marketplace
* Semver guarantees on the contracts

---

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). The shortest version: copy
the relevant `_template.yaml`, fill it in, run `lumadeck validate`,
add an example.

---

## Why this could win

ESPHome users love hardware but hate writing repetitive UI YAML.
LumaDeck makes the UI side reusable — you wire up GPIO once and pick
your widgets like a deck of cards.
