# LumaDeck — TODO

A universal ESPHome + LVGL UI package. The goal: a consumer device repo
should be able to `!include` themes, layouts, and widgets without ever
editing this package.

> Hardware reference target (consumed in a separate repo):
> Waveshare ESP32-S3-Touch-LCD-1.85C (round 360x360, capacitive touch).
> Nothing in this package may hard-code that hardware.

---

## Status (v0.1.0 — 2026-04-18)

* **v0.1 MVP**: complete.
* **v0.2**: ~80% done. Touch gestures + on-hardware verification + icon
  font loading still open.
* **v0.3**: CLI shipped early. Scaling, preview, widget registry still
  open.
* **v1.0**: not started.
* **Quality gates**: `make check` (yamllint + `lumadeck validate-all` +
  `pytest`) is green. 32 tests passing.

Anything below that is unchecked is a real follow-up.

---

## Next up (priority order)

The right next step is **functional widget completeness**, not more
docs or examples. Docs cover the contracts we already have; we need
the widgets behind those contracts to actually work end-to-end.

### P0 — unblocks everything else

1. ~~**Compile every example with `esphome config`.**~~  **DONE.**
   Verified against ESPHome 2026.4.0. The LilyGo device example
   passes (`INFO Configuration is valid!`); the 5 package-preview
   examples are correctly skipped because they don't define their
   own `display:` block. `make verify` is now a strict gate.

2. ~~**Flash `examples/lilygo-t-display-amoled.yaml` to the LilyGo
   board.**~~  **DONE.** Confirmed working. First-pass issues
   (text too small, landscape mode missing) are addressed in §11.

### P1 — functional gaps in the v0.1 widget set

2. ~~**`analog_clock.yaml`** — wire per-second hand rotation.~~
   **DONE.** Rewrote with rectangular hands rotated via
   `transform_angle` (0.1° units) around `transform_pivot_y` at the
   face center. Driven by an `interval: 1s` reading
   `id(ha_time).now()`.
3. ~~**`media_card.yaml`** — add volume slider + mute button.~~
   **DONE.** Added a horizontal LVGL `slider:` bound to
   `media_player.volume_set`, plus a mute toggle button driven by a
   `binary_sensor` mirroring the HA `is_volume_muted` attribute.
4. ~~**`album_art.yaml`** — HTTP fetcher.~~  **DONE.** Uses
   ESPHome's `online_image:` + `http_request:` components. A
   `text_sensor` watches the `entity_picture` attribute on the media
   player and calls `set_url()` + `component.update:` on state
   change. Configurable via `${ha_url}` and `${album_size}`.
5. ~~**`notification_toast.yaml`** — animate.~~  **DONE.** ESPHome
   doesn't expose `lv_anim_*` directly, so the slide is implemented
   as a `repeat:` loop with a lambda computing the y-offset per step
   (`${toast_anim_steps}` × `${toast_step_ms}` ms in each direction,
   tunable). Smooth enough at 8 × 25 ms = 200 ms total.

### P2 — close out v0.2

6. ~~**Touch gestures** in `packages/touch.yaml`.~~  **DONE.**
   `packages/touch.yaml` v0.2.0 ships software swipe detection:
   `lum_touch_press` / `lum_touch_update` / `lum_touch_release`
   scripts, fed by the consumer's `touchscreen:` callbacks, dispatch
   to `nav_next_page` / `nav_prev_page` when a horizontal swipe
   exceeds `${swipe_min_dist}` (default 60 px) within
   `${swipe_max_time_ms}` (default 500 ms). Wiring template +
   tuning notes in `docs/touch-gestures.md`. Wired into the LilyGo
   example and consumer-repo-template.
7. **Icon font rendering** — `font_icon` is declared but no widget
   actually uses it. Add an icon glyph to `nav_tabs.yaml` buttons as
   the first consumer.
8. ~~**Wire `${scale}` into widgets.**~~  **DONE — different
   approach.** ESPHome's Jinja-based substitutions don't support
   math (`${100 * scale}` is invalid), so a single multiplier was a
   non-starter. Instead, every widget now exposes its primary
   dimensions as `${var | default(N)}` inline (root width/height,
   key offsets, button sizes). Layouts override per screen via
   their `substitutions:` block. The wide_536x240 / tall_240x536
   layouts use this to retune media cards, nav tabs, status bars,
   etc. for the 1.91" AMOLED. Pattern documented in
   `docs/widget-contract.md` and `docs/layout-contract.md`.
   `${scale}` stays in the layout contract as an informational hint.

### P3 — new widgets

9. **`gauge.yaml`** — generic sensor → arc widget.
10. **`calendar_agenda.yaml`** — list of next N HA calendar events.

### P4 — polish (lowest priority)

* Per-widget READMEs (`widgets/<name>.md`)
* `docs/cli.md` full reference
* Screenshots / GIFs in README
* Markdown link checker in CI

---

## 0. Foundations

- [x] Define the public contract / "API" of the package
  - [x] List every `${substitution}` a theme MUST provide
        → `docs/theme-contract.md`
  - [x] List every `id:` a layout/widget MUST expose
        → `docs/layout-contract.md`, `docs/widget-contract.md`
  - [x] Document naming rules (snake_case, `lum_` prefix)
        → `docs/widget-contract.md`
  - [x] Add `CONTRIBUTING.md` describing the contract
- [x] Reconcile theme variable names — picked `bg/fg/accent/muted/...`,
      migrated `themes/*.yaml`, `widgets/clock.yaml`,
      `widgets/home_dashboard.yaml`.
- [x] Add a top-level `manifest.yaml` listing version, supported
      screen sizes, and required ESPHome version.
- [x] Add `CHANGELOG.md` and start tagging releases (`v0.1.0`).
- [x] Add `LICENSE` reference to README.
- [x] Add `.editorconfig` + `.yamllint.yaml` for consistency.

---

## 1. Repo hygiene

- [x] Fix README typos (`n- weather`, `n3. Wall thermostat panel`).
- [x] Remove duplicated/legacy "v0.1 Production Build" block from
      README.
- [x] Move long inline YAML in README into `docs/` and link to it.
- [x] Add GitHub issue + PR templates.
- [x] Add CI workflow (`.github/workflows/ci.yml`):
  - [x] `yamllint` on all `*.yaml`
  - [x] `lumadeck validate-all` against the contracts
  - [x] `pytest`
  - [x] `esphome config` dry-run against each `examples/*.yaml`
        (best-effort; examples include hardware-specific stubs)
  - [ ] Markdown link check on README/docs
- [x] Add `.gitattributes` for line endings.

---

## 2. Packages (`packages/`)

- [x] `core.yaml` — hardware-agnostic.
- [x] Make `core.yaml` board-agnostic
  - [x] Move `esp32:` block out to `packages/board_esp32s3.yaml`
  - [x] Allow consumer repo to choose `esp32` / `esp32c3` / `esp32s3`
  - [ ] Add `packages/board_esp32p4.yaml` (no devkit on hand to test)
- [x] `packages/fonts.yaml` — declares `font_xl/lg/md/sm/icon` from
      gfonts; sizes pulled from theme substitutions.
- [x] `packages/colors.yaml` — semantic color aliases on top of theme
      palette.
- [x] `packages/nav.yaml` — `script:` actions for page navigation.
- [x] `packages/ha.yaml` — Home Assistant service-call wrappers.
- [x] `packages/touch.yaml` — abstract touch-input flag globals.
- [x] `packages/display.yaml` — base LVGL config + reusable
      `style_definitions:`.

---

## 3. Themes (`themes/`)

- [x] `dark.yaml` — full theme contract.
- [x] `light.yaml`
- [x] `neon.yaml`
- [x] `themes/_template.yaml` — every key from the contract at its
      default value.
- [x] Document the required substitution keys
      (`docs/theme-contract.md`).
- [x] Add `themes/high_contrast.yaml` accessibility theme.
- [ ] Add seasonal / accent-only variants (optional, low priority).

---

## 4. Layouts (`layouts/`)

A layout = "how widgets are arranged on a given screen geometry".
It must NOT contain device-specific pins.

- [x] `round_360.yaml`
  - [x] Define safe drawing area (`safe_inset`) for circular masks
  - [x] Named regions: `region_top/center/bottom/left/right`
- [x] `square_240.yaml`
- [x] `wide_480x320.yaml`
- [x] `round_240.yaml`, `square_320.yaml`, `tall_240x320.yaml`
- [x] `layouts/_template.yaml` with the layout contract.
- [x] Introduce a scaling system: `${scale}` substitution declared by
      every layout.
- [x] Per-widget size scaling via inline `${var | default(N)}` —
      layouts override widget sizes directly. `${scale}` stays as a
      hint only. See `docs/widget-contract.md`.

---

## 5. Widgets (`widgets/`)

Each widget must:
- depend only on theme substitutions and documented ids
- be includable independently
- expose its own ids with a `lum_<name>_` prefix
- start with the contract header comment block

- [x] `clock.yaml` (rewritten on theme contract; date line; format
      configurable via substitutions).
- [x] `home_dashboard.yaml` (composite demo; updated).
- [x] `media_card.yaml` — title/artist + prev/play/next.
- [x] `weather.yaml`
- [x] `ring_slider.yaml` — brightness/volume; configurable target.
- [x] `icon_grid.yaml` — 6-slot scene grid; consumer wires `on_click`.
- [x] New widgets:
  - [x] `nav_tabs.yaml`
  - [x] `album_art.yaml` (placeholder card; see follow-up below)
  - [x] `thermostat.yaml`
  - [x] `light_button.yaml`
  - [x] `scene_button.yaml`
  - [x] `notification_toast.yaml` (top-layer overlay)
  - [x] `status_bar.yaml` (wifi/api/time)
  - [x] `progress_ring.yaml`
  - [x] `analog_clock.yaml` (face renders; hand rotation stubbed)
  - [ ] `calendar_agenda.yaml`
- [x] `widgets/_template.yaml`
- [ ] Per-widget README in `widgets/<name>.md` (or one `WIDGETS.md`).

### Widget follow-ups discovered during the build

See **Next up** at the top of this file for the priority ordering.

- [x] **(P1)** `analog_clock.yaml` — `transform_angle` hand rotation
      (v0.2.0). Awaits visual confirmation on hardware.
- [x] **(P1)** `album_art.yaml` — `online_image` + dynamic URL via
      `text_sensor.on_value` (v0.2.0). Awaits visual confirmation on
      hardware.
- [x] **(P1)** `media_card.yaml` — volume slider + mute toggle
      (v0.2.0).
- [x] **(P1)** `notification_toast.yaml` — stepwise slide animation
      via `repeat:` loop (v0.2.0).
- [ ] **(P3)** Add a generic `gauge.yaml` widget (sensor → arc).

---

## 6. Examples (`examples/`)

Examples are consumer-style YAMLs that prove the package works
end-to-end.

- [x] `round-clock.yaml`
- [x] `media-remote.yaml`
- [x] `room-controller.yaml`
- [x] `examples/waveshare-1.85c.yaml` — reference build for the
      hardware repo.
- [x] `examples/square-light-clock.yaml` — light theme + square
      layout, proves genericness.
- [ ] **Compile each example with `esphome config` against a real
      ESPHome version** to confirm `!extend page-id` and other LVGL
      merge patterns I used are valid.

---

## 7. Tools (`tools/`)

- [x] `tools/generate.py` — real CLI (`lumadeck new`):
  - [x] `lumadeck new <project> --screen round_360 --theme dark
        --widget clock ...`
  - [x] Emits a starter device YAML with correct includes
  - [x] Validates that the chosen layout / theme / widgets exist
- [x] `tools/lumadeck/validate.py` — `lumadeck validate <file>` and
      `lumadeck validate-all` enforce the theme/layout/widget
      contracts (with parametrised `pytest` coverage).
- [ ] `tools/preview/` — optional LVGL simulator preview (stretch).
- [x] Add `pyproject.toml` so tools install with `pip install -e .`.
- [x] Add `Pipfile` mirroring `pyproject.toml` for pipenv users.
- [x] Add `Makefile` task runner (`make help` for the catalogue).

---

## 8. Documentation

- [x] `docs/architecture.md`
- [x] `docs/theme-contract.md`
- [x] `docs/layout-contract.md`
- [x] `docs/widget-contract.md`
- [x] `docs/authoring-a-widget.md`
- [x] `docs/authoring-a-theme.md`
- [x] `docs/authoring-a-layout.md`
- [x] `docs/screen-sizes.md`
- [x] `docs/consumer-repo-guide.md`
- [ ] `docs/cli.md` — full reference for the `lumadeck` CLI
      (currently only documented via `--help`).

---

## 9. Roadmap alignment (from README)

### v0.1 (MVP) — DONE

- [x] core package solid + board-split
- [x] dark theme finalized
- [x] clock widget
- [x] media widget (basic)
- [x] round_360 layout usable end-to-end
- [x] one passing example: `examples/round-clock.yaml`

### v0.2 — mostly done

- [x] weather card
- [x] brightness ring slider
- [x] page navigation / nav tabs
- [x] `icon_grid` widget
- [x] Touch gestures abstraction — `packages/touch.yaml` v0.2.0 has
      software swipe detection wired to `nav_next_page` /
      `nav_prev_page`. See `docs/touch-gestures.md`.
- [ ] **Icon font** — `packages/fonts.yaml` declares `font_icon` from
      Material Symbols Outlined but no widget actually renders
      icon glyphs yet.
- [ ] **Edge-only swipe gestures** (v0.3 follow-up). Today swipes
      can fire mid-slider-drag if the user crosses the threshold;
      restricting swipes to `region_left` / `region_right` start
      points would eliminate the conflict entirely.

### v0.3 — partial

- [x] YAML generator CLI (`lumadeck new`)
- [ ] live theme preview
- [ ] resolution auto-scaling (`${scale}` declared but unused — see
      §4 follow-up)
- [ ] widget registry (machine-readable index) — `manifest.yaml`
      provides a static list; a runtime/HTTP registry is still open.

### v1.0

- [ ] HACS-style installer
- [ ] community widget marketplace
- [ ] semver guarantees on the package contract

---

## 10. Out of scope for this repo (belongs in consumer repos)

- Display / touch driver pin assignments
- Secrets (`secrets.yaml`)
- Device-specific `esphome:` name, board, framework choice
- Hardware buttons / encoders specific to a device

---

## 11. Cross-cutting follow-ups

Items that don't fit a single section:

- [x] Run every example through `esphome config` on a real ESPHome
      install. Confirmed against ESPHome 2026.4.0 — the LilyGo
      device example passes (`INFO Configuration is valid!`). CI now
      uses a strict `tools/verify_examples.py` that fails the build
      on any DEVICE-category example error.
- [x] Verified on hardware: the LilyGo T-Display-S3 AMOLED actually
      runs LumaDeck. First reported issues (text too small in
      portrait, no landscape mode) are addressed below.
- [x] **Landscape rotation on LilyGo AMOLED.** Resolved. The right
      syntax is `lvgl: rotation: 90` at the top of the LVGL block
      (NOT on the display: block, NOT on entries in lvgl: displays:).
      LVGL auto-rotates touchscreen coordinates to match. Documented
      in the ESPHome LVGL component page under "Display Rotation".
      The lilygo example + consumer-repo template are now landscape
      (`wide_536x240.yaml`) by default.
- [x] **Font sizes scaled for the 1.91" AMOLED.** The theme defaults
      (xl 48, lg 28, md 18, sm 14) are physically tiny on a 1.91"
      panel. Both `wide_536x240.yaml` and `tall_240x536.yaml` now
      override font_size_* (xl 56, lg 36, md 24, sm 18, icon 28).
      Pattern is reusable: any layout can override theme font sizes
      when the physical screen needs different sizing.
- [ ] Add a `tests/test_examples.py` that asserts each
      `examples/*.yaml` resolves all its substitutions.
- [ ] Add `pre-commit` config wiring `yamllint`, `ruff`, and
      `lumadeck validate-all`.
- [ ] Publish to PyPI once the contracts stabilise (v0.2+).
- [ ] Add screenshots / GIFs of each widget to the README.
