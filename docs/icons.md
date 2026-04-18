# Icons

LumaDeck uses [Material Symbols Outlined](https://fonts.google.com/icons)
as its icon font. The font is declared as `font_icon` in
`packages/fonts.yaml` and rendered via LVGL `label:` widgets.

## How it works

ESPHome's `font:` component embeds the requested glyphs into the
firmware at compile time — there's no runtime lazy-loading. Every
icon a widget references **must** be listed in the `glyphs:` block
of the `font_icon` font, or it'll render as a missing-glyph
placeholder.

`packages/fonts.yaml` ships with the canonical LumaDeck icon set
(every codepoint that at least one widget uses). Adding a new icon
to a custom widget = add the codepoint to `font_icon.glyphs:` and
reflash.

## Built-in icon set

| Codepoint | Material Symbols name | Used by                                    |
| --------- | --------------------- | ------------------------------------------ |
| `\uE88A`  | home                  | `nav_tabs` (Home button)                   |
| `\uE405`  | music_note            | `nav_tabs` (Media button)                  |
| `\uE0F0`  | lightbulb             | `nav_tabs` (Lights button)                 |
| `\uE8B8`  | settings              | `nav_tabs` (Settings button)               |
| `\uE037`  | play_arrow            | `media_card` (play state)                  |
| `\uE034`  | pause                 | `media_card` (pause while playing)         |
| `\uE044`  | skip_next             | `media_card` (next track)                  |
| `\uE045`  | skip_previous         | `media_card` (previous track)              |
| `\uE050`  | volume_up             | `media_card` (mute toggle, unmuted state)  |
| `\uE04F`  | volume_off            | `media_card` (mute toggle, muted state)    |
| `\uE63E`  | wifi                  | `status_bar` (wifi indicator)              |
| `\uE1DA`  | signal_wifi_off       | reserved (wifi-down indicator)             |
| `\uE2BF`  | cloud_done            | `status_bar` (HA API connected)            |
| `\uE2C1`  | cloud_off             | reserved (HA API disconnected)             |
| `\uE5C7`  | arrow_drop_up         | reserved (`thermostat` raise)              |
| `\uE5C5`  | arrow_drop_down       | reserved (`thermostat` lower)              |
| `\uE1FF`  | device_thermostat     | reserved                                    |
| `\uE518`  | light_mode            | reserved (theme toggle)                    |
| `\uF159`  | dark_mode             | reserved                                    |

## Using an icon in a widget

```yaml
- label:
    align: CENTER
    text_color: ${fg}
    text_font: font_icon
    text: "\uE037"   # play_arrow
```

Always include a comment naming the icon — bare codepoints are
opaque to anyone reading the widget later.

## Adding a new icon

1. Find the icon at <https://fonts.google.com/icons>. The "Code
   point" field on the right gives you the hex codepoint
   (e.g. `e88a` for `home`).
2. Add the codepoint to `packages/fonts.yaml` under the `font_icon`
   `glyphs:` list, with a comment naming the icon.
3. Reference it from your widget's `label.text` with the matching
   `text_font: font_icon`.
4. Reflash. The new glyph is now in the embedded font.

Each glyph adds a small amount of flash space (a few hundred bytes
to a few KB depending on size and complexity), so don't add the
whole 2,500-icon catalogue — just the ones you'll actually use.

## Swapping the icon family

If you'd rather use Material Icons (the older filled style) or a
custom icon font, override `font_icon` in your consumer device YAML:

```yaml
font:
  - file: "gfonts://Material Icons"
    id: font_icon
    size: ${font_size_icon}
    glyphs: [ "\uE037", "\uE034", ... ]
```

The codepoints differ between font families, so you'll need to
re-pick them from the new font's catalogue.
