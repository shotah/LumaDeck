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
* New `examples/lilygo-test-rig.yaml` includes every LumaDeck widget
  on a single device (visually it's a mess, but every widget's YAML
  is verified to parse against ESPHome's LVGL schema).

### Consumer-driven hardening (Waveshare 1.85C bring-up)

A real consumer repo wired the Waveshare ESP32-S3-Touch-LCD-1.85C
(round 360×360, ST77916/QSPI, CST816 touch, TCA9554 expander,
PCM5101 I²S DAC) onto LumaDeck and surfaced a stack of issues. All
fixed:

* **Five layouts now declare `climate_page`.** `round_240`,
  `round_360`, `square_240`, `square_320`, and `tall_240x320` were
  missing the page that `packages/nav.yaml`'s `nav_goto_climate`
  references — including those layouts plus `nav.yaml` crashed
  `esphome config`. `layouts/_template.yaml` updated to ship all
  five pages so new layouts start contract-compliant.
* **Layout contract upgraded.** `docs/layout-contract.md` now states
  that all five pages are required (not optional);
  `tools/lumadeck/contract.py` matches.
* **Validator cross-check.** `tools/lumadeck/validate.py` parses
  every `lvgl.page.show:` reference in `packages/nav.yaml` and
  asserts each layout declares the page. `lumadeck validate-all`
  fails loudly if a future layout addition skips a page.
* **`packages/audio.yaml`** — opt-in I²S DAC abstraction. Consumer
  declares the `i2s_audio:` bus + `audio_dout_pin` substitution;
  the package supplies a `lum_speaker` sink. Mirrors the
  `display:` / `touchscreen:` split.
* **`packages/backlight.yaml`** — wraps the common LEDC PWM →
  monochromatic-light pattern for panel backlights. Consumer sets
  `${backlight_pin}` (and optionally `${backlight_freq}`); package
  supplies `output: lum_backlight` and `light: lum_backlight_light`
  (HA-controllable, named after the device).
* **`widgets/notification_sound.yaml`** — script-only widget exposing
  `lum_notify_chime`. Generates a short sine-wave PCM buffer at
  runtime and plays it through `lum_speaker`. Pairs with
  `notification_toast`. Tunable via `${notify_freq_hz}`,
  `${notify_duration_ms}`, `${notify_amplitude}` substitutions.
* **`docs/displays-with-io-expander-reset.md`** — new doc covering
  the TCA9554 / PCA9554 reset-line pattern. Includes the
  `pca9554:`-vs-`tca9554:` naming gotcha, a worked example, and
  the common pitfalls (inverted reset, output mode required, I²C
  address collisions, reset timing).
* **`examples/waveshare-1.85c.yaml` is no longer a stub.** Full
  hardware block (ST77916 init sequence transcribed verbatim from
  Espressif's `esp_lcd_st77916.c`, TCA9554 expander wiring, QSPI
  bus, CST816 touch with expander reset, GPIO0 boot button, I²S
  audio bus, USB_SERIAL_JTAG logging override). Passes
  `esphome config` against ESPHome 2026.04 — first-light flash
  pending. Uses the new `packages/backlight.yaml` and
  `packages/audio.yaml`, plus the new `notification_sound` widget.

`make verify` count: 3 DEVICE examples passing
(`lilygo-t-display-amoled`, `lilygo-test-rig`, `waveshare-1.85c`),
0 failures.

### Icons + edge swipe

* `packages/fonts.yaml` now ships a documented set of 19 Material
  Symbols Outlined codepoints (home, music_note, lightbulb, settings,
  play_arrow, pause, skip_next/previous, volume_up/off, wifi,
  signal_wifi_off, cloud_done/off, arrow_drop_up/down,
  device_thermostat, light_mode, dark_mode). New `docs/icons.md`
  documents the catalogue and how to add new glyphs.
* `widgets/nav_tabs.yaml` → v0.3.0. Replaces text labels (`home`,
  `media`, etc.) with proper icon glyphs.
* `widgets/media_card.yaml` → v0.4.0. Transport buttons render
  skip_previous / play_arrow / skip_next icons; the play button
  auto-swaps to pause while the media_player is in `playing` state
  (via a new `text_sensor`). Mute button shows volume_up /
  volume_off based on HA `is_volume_muted`.
* `widgets/status_bar.yaml` → v0.4.0. wifi + cloud_done icons
  replace the placeholder "wifi" / "api" text.
* `packages/touch.yaml` → v0.3.0. Swipe gestures now require the
  start point to be within `${swipe_edge_px}` (default 40 px) of
  the left or right screen edge. Eliminates the slider/arc drag
  conflict — horizontal drags in the middle of the screen no longer
  fire navigation events. Set `swipe_edge_px: ${screen_w}` to
  restore the v0.2 anywhere-swipe behaviour.
* `docs/touch-gestures.md` updated with the new edge zone tuning
  knob and how to disable it.
* `layouts/wide_536x240.yaml`: `media_h` trimmed from 200 to 180 so
  the title/artist labels in `media_card` v0.4.0 don't get squeezed.

### Per-widget size scaling

* Every widget now exposes its primary dimensions (root
  width/height, button sizes, label widths, key offsets) as
  inline-default substitutions using Jinja's `${var | default(N)}`
  filter. Layouts override these directly to fit different physical
  panels.
* Documented two distinct substitution patterns in
  `docs/widget-contract.md`:
  * **Inline default (`${var | default(N)}`)** — for sizes/offsets
    a layout may override. Doesn't claim the substitution name, so
    later includes can't accidentally beat the override.
  * **`substitutions:` block** — for per-instance configuration
    (entity ids, labels, format strings).
* `layouts/wide_536x240.yaml` and `layouts/tall_240x536.yaml` now
  override widget sizes (media cards, nav tabs, status bars, etc.)
  to fit the 1.91" AMOLED's 240 px short axis.
* `docs/layout-contract.md` clarifies that `${scale}` is an
  informational hint, not a math multiplier — ESPHome's
  Jinja-based substitutions don't support arbitrary math at config
  time. Per-screen scaling is done via the per-widget overrides
  above.
* Widgets bumped: `clock` → 0.2.0, `status_bar` → 0.3.0,
  `nav_tabs` → 0.2.0, `weather` → 0.2.0, `light_button` → 0.2.0,
  `media_card` → 0.3.0, `thermostat` → 0.2.0,
  `notification_toast` → 0.3.0, plus `analog_clock`,
  `progress_ring`, `ring_slider`, `album_art` migrated to inline
  defaults.

### Touch gestures

* `packages/touch.yaml` → v0.2.0. Software swipe detection.
  Three new scripts (`lum_touch_press` / `lum_touch_update` /
  `lum_touch_release`) consume raw touchscreen callbacks and
  dispatch horizontal swipes to `nav_next_page` / `nav_prev_page`.
  Configurable via `${swipe_min_dist}` (default 60 px) and
  `${swipe_max_time_ms}` (default 500 ms). Vertical swipes are
  reserved for v0.3.
* New `docs/touch-gestures.md` with the consumer wiring template
  and tuning notes.
* Both `examples/lilygo-t-display-amoled.yaml` and
  `consumer-repo-template/device.yaml` now wire `on_touch` /
  `on_update` / `on_release` into the new scripts. Legacy
  `touch_mark_active` / `touch_mark_idle` aliases retained so
  pre-0.2 device YAMLs don't break.

### Widget upgrades

* `widgets/analog_clock.yaml` → v0.2.0. Hand rotation now actually
  works: rectangular hands rotated each second via `transform_angle`
  (0.1° units) around `transform_pivot_y` at the face center,
  driven by `id(ha_time).now()`.
* `widgets/album_art.yaml` → v0.2.0. Pulls the current
  `${ha_media_player}.entity_picture` from Home Assistant via
  `online_image` + `http_request`, prepending `${ha_url}` for
  relative paths. Updates the LVGL `image:` widget on every track
  change.
* `widgets/media_card.yaml` → v0.2.0. Added a horizontal LVGL
  `slider:` bound to `media_player.volume_set` and a mute toggle
  whose color tracks the HA `is_volume_muted` attribute via a
  `binary_sensor`.
* `widgets/notification_toast.yaml` → v0.2.0. Slide-in / slide-out
  is now animated via a `repeat:` loop computing the y position per
  step (8 × 25 ms ≈ 200 ms each way; all timings tunable via
  `${toast_anim_steps}` / `${toast_step_ms}`).

### Hardware-confirmed and fixed

* **LumaDeck verified running on the LilyGo T-Display-S3 AMOLED.**
  First-pass issues from the bring-up:
  * **Landscape rotation now works.** ESPHome's LVGL component
    accepts `rotation:` as a top-level key (`lvgl: rotation: 90`),
    NOT on the `display:` block or on entries in `lvgl: displays:`.
    Touchscreen coordinates are auto-rotated. The lilygo example
    and consumer-repo template default to landscape
    (`wide_536x240.yaml`); switch to `tall_240x536.yaml` and drop
    the `rotation:` line for portrait.
  * **Text now scales for the 1.91" panel.** Both
    `layouts/wide_536x240.yaml` and `layouts/tall_240x536.yaml`
    override the theme font sizes (xl 56, lg 36, md 24, sm 18,
    icon 28) so text is readable at arm's length. Establishes the
    pattern: layouts MAY override theme font_size_* substitutions
    when the physical screen needs different sizing.
* `widgets/analog_clock.yaml` switched from `transform_angle` to
  `transform_rotation` (the older property name is deprecated in
  ESPHome 2026.x per the LVGL component docs).

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
