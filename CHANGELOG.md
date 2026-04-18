# Changelog

All notable changes to LumaDeck are tracked here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

* `Makefile` with cross-platform targets for setup, validation,
  testing, scaffolding, and packaging. Run `make help` for the list.
* `Pipfile` mirroring `pyproject.toml` for pipenv users.
* `[verify]` extras group in `pyproject.toml` (and matching
  `dev-packages` entry in `Pipfile`) installing ESPHome locally.
* `make verify` target running `esphome config` against every
  `examples/*.yaml`, plus `docs/verifying-examples.md` walkthrough
  covering install, expected output, and common failure modes.
* New layouts `layouts/tall_240x536.yaml` (portrait, native) and
  `layouts/wide_536x240.yaml` (landscape, rotated) for the LilyGo
  T-Display-S3 AMOLED 1.91". The example + consumer-repo template
  default to landscape since the aspect ratio suits it better.
* New example `examples/lilygo-t-display-amoled.yaml` — fully
  self-contained device YAML with `qspi_dbi` / RM67162 display and
  `cst816` touch, pin map taken from the upstream
  [LilyGo-AMOLED-Series](https://github.com/Xinyuan-LilyGO/LilyGo-AMOLED-Series)
  library.
* New `consumer-repo-template/` directory — drop-in starter for a
  hardware repo that consumes LumaDeck as a git submodule.
  Includes `device.yaml`, `secrets.example.yaml`, `.gitignore`, and a
  README walking through the workflow.
* `manifest.yaml` now lists `reference_hardware:` so a future
  installer / registry can discover supported panels.
* `examples/secrets.example.yaml` — committed placeholder secrets so
  `esphome config` (and `make verify`) can resolve `!secret` calls
  without anyone editing real credentials. `make verify` materialises
  `examples/secrets.yaml` (gitignored) from this template on first
  run. CI does the same.
* `tools/verify_examples.py` — drives `make verify` (and the Pipenv
  `verify` script + the CI workflow). Categorises files into DEVICE
  (has `display:` block, gets validated) vs PREVIEW (skipped with
  explanatory note), so the package-only examples don't false-fail.

### Verified

* **`esphome config` passes** for the LilyGo T-Display-S3 AMOLED
  example on ESPHome 2026.4.0. Confirms `!extend page-id`, the
  `qspi_dbi`/RM67162 driver, the `cst816` touch platform, and every
  widget's LVGL syntax all work end-to-end.

### Known limitations

* Landscape rotation on the LilyGo AMOLED is deferred — ESPHome
  2026.4.0 rejects `rotation:` on both the `display:` block (when
  bound to LVGL) and on entries in `lvgl: displays:`. The example
  uses portrait `tall_240x536.yaml` until the right rotation syntax
  is identified. Tracked in `todo.md` §11.

### Changed

* `CONTRIBUTING.md` and the PR template now point at `make check` as
  the single entry point for running all quality gates.
* README and CONTRIBUTING quick-starts now document the verify path
  alongside the standard dev install.

## [0.1.0] - 2026-04-18

### Added

* Hardware-agnostic `packages/core.yaml` with board split
  (`board_esp32.yaml`, `board_esp32s3.yaml`, `board_esp32c3.yaml`).
* Standard ESPHome packages: `fonts`, `colors`, `display`, `nav`,
  `ha`, `touch`.
* Theme contract documented in `docs/theme-contract.md`. Themes:
  `dark`, `light`, `neon`, `high_contrast`, `_template`.
* Layout contract documented in `docs/layout-contract.md`. Layouts:
  `round_240`, `round_360`, `square_240`, `square_320`,
  `tall_240x320`, `wide_480x320`, `_template`.
* Widget contract documented in `docs/widget-contract.md`. Widgets:
  `clock`, `analog_clock`, `status_bar`, `nav_tabs`, `media_card`,
  `album_art`, `weather`, `ring_slider`, `progress_ring`,
  `icon_grid`, `light_button`, `scene_button`, `thermostat`,
  `notification_toast`, `home_dashboard`, `_template`.
* Examples: `round-clock`, `media-remote`, `room-controller`,
  `waveshare-1.85c`, `square-light-clock`.
* `lumadeck` CLI (`tools/lumadeck/`) with `list`, `new`, `validate`,
  `validate-all` subcommands.
* Pytest suite covering every theme, layout, and widget against its
  contract.
* Authoring guides in `docs/` (theme, layout, widget) and
  `docs/consumer-repo-guide.md` for hardware repos.
* Project metadata: `manifest.yaml`, `pyproject.toml`,
  `.editorconfig`, `.yamllint.yaml`, `.gitattributes`, GitHub issue
  and PR templates, CI workflow.

### Changed

* `packages/core.yaml` no longer hard-codes a board.
* `widgets/clock.yaml` and `widgets/home_dashboard.yaml` migrated
  from the old `color_*` substitution names to the canonical
  `bg/fg/accent/...` theme contract.

[Unreleased]: https://github.com/shotah/LumaDeck/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/shotah/LumaDeck/releases/tag/v0.1.0
