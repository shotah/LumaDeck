# Consumer repo guide

LumaDeck is meant to be **consumed**, not forked. Your hardware repo
should reference this package and add only the bits unique to your
panel: the `display:` driver, the `touchscreen:` driver, and any
device-specific GPIO (encoders, hardware buttons, LEDs).

## Recommended layout

```
my-panel-firmware/
├── secrets.yaml            # gitignored
├── secrets.example.yaml    # commit this template
├── .gitignore              # ignores secrets.yaml + .esphome/
├── device.yaml             # your device YAML
└── lumadeck/               # git submodule or symlink to this repo
```

A drop-in template for this layout lives at
[`../consumer-repo-template/`](../consumer-repo-template/) — copy it
out of the LumaDeck checkout and you have a working starter repo.

## Minimal device YAML

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

# ---- hardware (you write this) ----
spi:
  - id: lcd_spi
    type: quad
    clk_pin: GPIO40
    data_pins: [GPIO46, GPIO45, GPIO42, GPIO41]

display:
  - platform: <your_panel_driver>
    id: lum_display
    spi_id: lcd_spi
    cs_pin: GPIO21
    reset_pin: GPIO39
    dimensions: { width: 360, height: 360 }
    auto_clear_enabled: false

i2c:
  - id: bus_a
    sda: GPIO11
    scl: GPIO10

touchscreen:
  - platform: cst816
    id: lum_touchscreen
    i2c_id: bus_a
    interrupt_pin: GPIO4
    reset_pin: GPIO5
```

## Override patterns

### Pick a different theme

```yaml
packages:
  theme: !include lumadeck/themes/neon.yaml
```

### Tweak just one substitution

Define your own substitutions BEFORE the packages block and they'll
beat the package defaults:

```yaml
substitutions:
  accent: "0xFF00C8"   # override the theme

packages:
  theme: !include lumadeck/themes/dark.yaml
```

### Bind a widget to your entities

Widgets like `media_card.yaml` read their entity id from a substitution
(`ha_media_player`). Set it at the device level:

```yaml
substitutions:
  ha_media_player: "media_player.kitchen_speaker"
```

### Wire icon_grid buttons to your scripts

`widgets/icon_grid.yaml` exposes `lum_icongrid_btn_1..6`. Add
`on_click:` handlers to them in your device YAML (ESPHome merges them
in):

```yaml
lvgl:
  pages:
    - id: !extend home_page
      widgets:
        - button:
            id: lum_icongrid_btn_1
            on_click:
              - homeassistant.service:
                  service: scene.turn_on
                  data: { entity_id: scene.movie_time }
```

## Updating LumaDeck

If you're using a git submodule:

```
cd lumadeck && git pull && cd ..
git add lumadeck && git commit -m "bump LumaDeck"
```

Watch the [CHANGELOG](../CHANGELOG.md) for breaking changes — all
contract changes will be in a major version bump.

## Out of scope for LumaDeck

* Pin assignments
* Display / touch drivers
* Secrets
* `esphome:` name (set via `${device_name}` substitution instead)
* Hardware buttons / encoders specific to your device
