# Authoring a layout

Layouts describe screen geometry. They never reference hardware (no
pins, no display drivers).

## When you need a new layout

Add one when you have a new screen size or shape that isn't covered
by `layouts/*.yaml`. Don't add device-specific layouts; if two
240x240 round panels both exist, they share `round_240.yaml`.

## 1. Copy the template

```
cp layouts/_template.yaml layouts/round_480.yaml
```

## 2. Set the geometry substitutions

```yaml
substitutions:
  screen_w:       "480"
  screen_h:       "480"
  screen_shape:   "round"
  screen_radius:  "240"
  scale:          "1.3"
  safe_inset:     "70"   # round only
```

`scale` is a multiplier widgets MAY use to size themselves relative
to the screen. The default theme assumes `scale: 1.0` ~= 360 px.

## 3. Define `home_page` and named regions

Every layout MUST define `home_page`. Region anchors are invisible
`obj`s with ids `region_top`, `region_center`, `region_bottom`,
`region_left`, `region_right`. Widgets `align_to` these.

For round screens, position the regions inside the inscribed square
using `safe_inset`. For square/wide/tall screens, the regions sit on
the edges.

## 4. Add optional pages

Include `media_page`, `lights_page`, `climate_page`, `settings_page`
as needed so widgets that target those pages have somewhere to attach.

## 5. Validate

```
lumadeck validate layouts/round_480.yaml
```

## 6. Document the screen

Add a row to [`screen-sizes.md`](./screen-sizes.md).
