# Displays with I/O-expander reset lines

A growing slice of ESP32 dev boards — Waveshare's 1.85", 2.8", and 4B
round/square panels, several Guition AMOLED boards, some LilyGo
variants — wire the LCD reset (and often touch reset, SD card CS,
backlight enable, etc.) to a **TCA9554 / PCA9554 I²C GPIO expander**
rather than to a real ESP32 GPIO. The ESP32 talks to the expander
over I²C; the expander toggles the actual reset line.

This page documents how to wire that pattern through ESPHome's
display and touchscreen platforms so the reset line gets toggled
correctly on boot. It's the kind of thing that's obvious once you've
done it once but throws schema errors that send you down the wrong
trail otherwise.

## When you'll hit this

You'll know you're in this case if:

* The board's schematic shows `LCD_RST` or `TP_RST` going to a chip
  labelled `TCA9554PWR`, `PCA9554`, or similar — not directly to
  the ESP32.
* Setting `reset_pin: GPIOXX` in the `display:` block crashes with
  "GPIO already used" or behaves like the reset line is floating.
* The board's official Arduino code does `expander.write(EXIO_2,
  LOW); delay(10); expander.write(EXIO_2, HIGH);` somewhere during
  init.

Boards I've personally verified or seen this pattern on:

| Board | Expander | LCD_RST | TP_RST |
| ----- | -------- | ------- | ------ |
| Waveshare ESP32-S3-Touch-LCD-1.85C | TCA9554PWR @ 0x20 | EXIO2 | EXIO1 |
| Waveshare ESP32-S3-Touch-LCD-2.8C | TCA9554PWR @ 0x20 | EXIO2 | EXIO1 |
| Waveshare ESP32-S3-Touch-LCD-4B   | TCA9554PWR @ 0x20 | EXIO5 | EXIO0 |

(Always cross-check against your board's schematic — pin assignments
have varied across hardware revisions of the same SKU.)

## Naming gotcha: `pca9554` vs `tca9554`

ESPHome (as of 2026.04) ships a `pca9554:` platform that handles
**both** PCA9554 *and* TCA9554 — they share the same command
interface. There is **no** `tca9554:` platform. Despite every
datasheet, schematic, and Waveshare wiki page calling the chip a
TCA9554, you write `pca9554:` in your YAML.

This is a 5-minute search trap that's caught both me and at least
one Waveshare employee writing example code. Save yourself the time.

## Worked example (Waveshare 1.85C)

The full version lives in
[`../examples/waveshare-1.85c.yaml`](../examples/waveshare-1.85c.yaml);
the relevant blocks:

```yaml
i2c:
  - id: bus_a
    sda: GPIO11
    scl: GPIO10
    frequency: 400kHz

# Both PCA9554 and TCA9554 use this platform — no separate component.
pca9554:
  - id: lum_io_expander
    address: 0x20
    i2c_id: bus_a

display:
  - platform: qspi_dbi
    id: lum_display
    # ... cs_pin, dimensions, init_sequence, etc. ...
    reset_pin:
      pca9554: lum_io_expander   # route reset through the expander
      number: 2                  # EXIO2 on the TCA9554PWR
      mode:
        output: true
      inverted: true             # reset is active-low

touchscreen:
  - platform: cst816
    id: lum_touchscreen
    i2c_id: bus_a
    interrupt_pin: GPIO4
    reset_pin:
      pca9554: lum_io_expander   # touch reset is also expander-side
      number: 1                  # EXIO1
      mode:
        output: true
      inverted: true
```

Anything else routed through the same expander — SD card CS,
backlight enable, RGB LED, etc. — uses the same `pca9554:` pin
schema with a different `number:`.

## Pitfalls

* **Don't put `pca9554:` after `display:` / `touchscreen:`** in the
  same file. ESPHome resolves component dependencies in YAML order
  in some versions; the expander needs to exist before anything
  references it. Declaring the I²C bus and the expander block
  immediately after `i2c:` is the safe order.
* **`inverted: true` matters.** The reset line on virtually every
  panel I've seen is active-low. Forget the `inverted: true` and
  the panel sits in permanent reset (looks dead, no init sequence
  ever runs) or never resets at all (random init failures).
* **`mode.output: true` is required.** The expander defaults pins to
  input. Without `mode.output: true` the expander never drives the
  pin, regardless of what `inverted:` says.
* **Watch for I²C address collisions.** TCA9554 addresses are
  configurable via A0/A1/A2 strap pins — `0x20` is the common
  default but cheap aliexpress boards sometimes ship with `0x38` or
  `0x3F`. If `i2c.scan: true` shows nothing at `0x20`, walk the
  range with `i2cdetect`.
* **Reset timing.** ESPHome's `reset_pin:` toggles once at boot.
  Most ICs need a low pulse of ≥10 ms — that's the platform default
  and you don't need to override it. If your panel still doesn't
  init, try increasing it via `reset_duration:` (some platforms) or
  hand-rolling the toggle in `on_boot:` before initialising the
  display.

## See also

* [`consumer-repo-guide.md`](./consumer-repo-guide.md) — overall
  pattern for hardware repos
* [`../examples/waveshare-1.85c.yaml`](../examples/waveshare-1.85c.yaml)
  — full reference build with expander + QSPI + CST816 touch + I²S audio
* ESPHome [pca9554 platform docs](https://esphome.io/components/pca9554.html)
