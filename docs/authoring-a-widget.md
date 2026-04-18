# Authoring a widget

This walks through adding a new widget end-to-end.

## 1. Pick a name

Use snake_case. Match the file name. Example: `widgets/battery_pill.yaml`.

## 2. Copy the template

```
cp widgets/_template.yaml widgets/battery_pill.yaml
```

## 3. Fill in the header comment

Every widget MUST start with the contract header. See
[`widget-contract.md`](./widget-contract.md). The validator parses
this header and will fail without it.

```yaml
# ---------------------------------------------------------------
# widget: battery_pill
# version: 0.1.0
# reads:        ${bg_alt} ${fg} ${accent} ${border} ${font_sm}
# targets:      home_page
# exposes:      lum_battery_root lum_battery_label
# ha_entities:  ${ha_battery_sensor:-sensor.phone_battery}
# ha_services:  none
# config:       ${battery_label:-bat}
# ---------------------------------------------------------------
```

## 4. Add the LVGL block

Anchor to a layout-defined region whenever possible (see
[`layout-contract.md`](./layout-contract.md)) instead of using raw
x/y. Use the `lum_<name>_` id prefix for everything you create.

```yaml
lvgl:
  pages:
    - id: !extend home_page
      widgets:
        - obj:
            id: lum_battery_root
            align_to:
              id: region_top
              align: CENTER
              x: -90
            width: 64
            height: 22
            bg_color: ${bg_alt}
            border_color: ${border}
            border_width: ${border_w}
            radius: ${radius_pill}
            widgets:
              - label:
                  id: lum_battery_label
                  align: CENTER
                  text_color: ${fg}
                  text_font: font_sm
                  text: "--%"
```

## 5. Wire any data sources

Pull HA state via `sensor:` / `text_sensor:` with
`platform: homeassistant`. Update LVGL labels in `on_value:`.

```yaml
sensor:
  - platform: homeassistant
    id: lum_battery_src
    entity_id: ${ha_battery_sensor:-sensor.phone_battery}
    on_value:
      - lvgl.label.update:
          id: lum_battery_label
          text: !lambda |-
            return (std::to_string((int)x) + "%");
```

## 6. Validate

```
lumadeck validate widgets/battery_pill.yaml
```

## 7. Add an example

Drop the include into `examples/round-clock.yaml` (or write a new
example). Run `esphome config examples/round-clock.yaml` to confirm
ESPHome can compile against it.

## 8. (Optional) Document

Either add a section to `WIDGETS.md` or write `widgets/battery_pill.md`.
