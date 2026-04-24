# LumaDeck — Upstream TODO from the consumer repo

A list of fixes and follow-ups discovered while wiring up a real
**Waveshare ESP32-S3-Touch-LCD-1.85C** (round 360x360 + speaker)
device YAML alongside the existing LilyGo T-Display-S3 AMOLED.

> **STATUS — landed upstream.** Every P0/P1/P2 item below has been
> resolved in the upstream LumaDeck repo. Consumer repo can:
>
> 1. Bump the `lumadeck/` submodule pointer.
> 2. Delete the `lvgl: pages: - id: climate_page` workaround from
>    its waveshare YAML (round_360 layout now ships it).
> 3. Switch `output:` + `light:` blocks for the backlight to
>    `!include lumadeck/packages/backlight.yaml` plus
>    `${backlight_pin}` substitution.
> 4. Switch `speaker:` block to `!include lumadeck/packages/audio.yaml`
>    plus `${audio_dout_pin}` substitution; keep the `i2s_audio:`
>    block (hardware-side).
> 5. Optionally `!include lumadeck/widgets/notification_sound.yaml`
>    and call `script.execute: lum_notify_chime` for chimes.
> 6. Delete this file (or just the items below — P3 still has
>    nice-to-haves).
>
> Reference upstream change set: see CHANGELOG.md
> "Consumer-driven hardening (Waveshare 1.85C bring-up)".

---

## P0 — bugs that break real consumers today

### 1. Five layouts are missing `climate_page`  ✅ DONE

`packages/nav.yaml` defines `nav_goto_climate` which calls
`lvgl.page.show: climate_page`. Layouts that didn't declare the
page crashed `esphome config`.

**Fix shipped:** added `climate_page` placeholder to `round_240`,
`round_360`, `square_240`, `square_320`, and `tall_240x320`.
`layouts/_template.yaml` now declares all five so new layouts start
contract-compliant.

### 2. `make verify` is too lenient — should have caught #1  ✅ DONE (clarification)

Already addressed before this TODO was written:
`tools/verify_examples.py` is strict (no `|| true`). The reason #1
slipped through was structural — none of the existing examples
combined `nav.yaml` with one of the affected layouts.

**Real fix shipped:** see #8 — the validator now cross-checks
`nav.yaml` page references against every layout, so this class of
bug can't silently regress.

---

## P1 — turn the Waveshare 1.85C into a real reference build

### 3. Promote `examples/waveshare-1.85c.yaml` from stub to working  ✅ DONE

The example now ships the full hardware block (ST77916 init
sequence, TCA9554 expander wiring, QSPI bus, CST816 touch with
expander reset, GPIO0 boot button, USB_SERIAL_JTAG logger override,
I²S audio bus). Includes the new `packages/backlight.yaml`,
`packages/audio.yaml`, and `widgets/notification_sound.yaml`.

Passes `esphome config` against ESPHome 2026.04. Header carries the
"NOT yet bring-up tested" caveat with notes on which knobs
(`color_order`, `invert_colors`) might need flipping on first light.

### 4. Add `docs/displays-with-io-expander-reset.md`  ✅ DONE

New doc covering when you'll hit this pattern, the
`pca9554`-vs-`tca9554` naming gotcha, a worked example lifted from
the Waveshare YAML, the table of boards using this pattern, and
common pitfalls (active-low reset, `mode.output: true` requirement,
I²C address collisions, reset timing).

### 5. Add `packages/audio.yaml` (I2S DAC abstraction)  ✅ DONE

Shipped as suggested. Consumer declares the `i2s_audio:` bus +
`audio_dout_pin` substitution; package supplies the `lum_speaker`
sink with `audio_channel` (default `mono`) override.

### 6. Add a `widgets/notification_sound.yaml` once `audio.yaml` lands  ✅ DONE

Script-only widget. Calling `script.execute: lum_notify_chime`
generates a short sine-wave PCM buffer in lambda and plays it via
`lum_speaker`. Configurable via `${notify_freq_hz | default(880)}`,
`${notify_duration_ms | default(120)}`, `${notify_amplitude | default(8000)}`.

---

## P2 — contract / docs hardening

### 7. `docs/layout-contract.md` should formalise the page list  ✅ DONE

Updated. The contract now states explicitly that all five pages
(`home_page`, `media_page`, `lights_page`, `climate_page`,
`settings_page`) are required, with a note that "a page with no
widgets is fine — `- id: foo_page  bg_color: ${bg}` is enough".
`tools/lumadeck/contract.py` matches.

### 8. `lumadeck validate-all` should cross-check nav ↔ layouts  ✅ DONE

`validate-all` now starts with a "nav <-> layout cross-check" pass
that parses every `lvgl.page.show:` ref in `packages/nav.yaml` and
asserts each layout declares the page. Fails the build on the same
class of bug as #1 if it ever recurs.

### 9. `widgets/backlight.yaml` (consume the new substitutions)  ✅ DONE — moved to `packages/backlight.yaml`

Renamed during implementation. The output + light blocks aren't
LVGL widgets, they're hardware abstractions, so they belong under
`packages/`. Consumer wiring matches what was sketched: set
`${backlight_pin}` (and optionally `${backlight_freq}`) at the
device level, include the package.

A future `widgets/backlight_slider.yaml` (LVGL ring slider that
drives `lum_backlight_light`) is logged as a v0.3 follow-up.

### 10. Add `examples/waveshare-1.85c.yaml` to `make verify` test set  ✅ DONE

Automatic — the verifier picks up any `examples/*.yaml` with a
top-level `display:` block. Now passing alongside
`lilygo-t-display-amoled` and `lilygo-test-rig`.

---

## P3 — nice-to-have, low priority (still open upstream)

* **`docs/screen-sizes.md`** — add a "round 360" worked example
  pointing at the Waveshare 1.85C and the consumer repo template.
* **`themes/round_optimised.yaml`** — none of the themes have been
  visually verified on a round panel. Worth a variant that respects
  the 51 px `safe_inset` from `round_360.yaml` (larger fonts,
  thicker borders so widgets stay legible inside the inscribed
  square). Punt until first-light reveals what's actually wrong.
* **`widgets/analog_clock.yaml`** — already implemented upstream
  with `transform_rotation` per-second hand updates; needs a round
  panel (Waveshare) to visually verify the pivot math.
* **`widgets/backlight_slider.yaml`** — LVGL ring slider that drives
  `lum_backlight_light`. Pairs with the new `packages/backlight.yaml`
  and gives the "brightness page" a UI surface.

---

## How to migrate this into LumaDeck

This was the proposed PR breakdown. Upstream landed it as a single
batch (PR-1 through PR-6 condensed) under "Consumer-driven hardening
(Waveshare 1.85C bring-up)". For future consumer-side TODOs of
similar shape, the split below is still a good template:

1. **PR-1** — Layouts: add `climate_page` placeholders to the five
   layouts that lack it (#1). One file edit each, ~5 lines per file.
2. **PR-2** — `make verify` strict mode + CI tightening (#2).
3. **PR-3** — Layout contract update + validator extension
   (#7, #8). Pure docs + tests.
4. **PR-4** — Promote `examples/waveshare-1.85c.yaml` to a working
   driver block (#3).
5. **PR-5** — Docs: `displays-with-io-expander-reset.md` (#4).
6. **PR-6** — `packages/audio.yaml` + `packages/backlight.yaml`
   (#5, #9).
7. **PR-7** — `widgets/notification_sound.yaml` (#6).
