# Authoring a theme

A theme is just substitutions. Five-minute job.

## 1. Copy the template

```
cp themes/_template.yaml themes/sunset.yaml
```

## 2. Override the keys you care about

The template contains every key from
[`theme-contract.md`](./theme-contract.md) at its default value.
Override any subset. Anything you leave alone keeps the default.

The minimum useful theme overrides the color palette:

```yaml
substitutions:
  bg:         "0x14080A"
  bg_alt:     "0x261015"
  fg:         "0xFFE6E0"
  fg_muted:   "0x9C7A82"
  accent:     "0xFF6B35"
  accent_alt: "0xFFAA66"
  success:    "0x6BCB77"
  warn:       "0xFFD93D"
  error:      "0xE63946"
  border:     "0x3A1E26"
```

## 3. Validate

```
lumadeck validate themes/sunset.yaml
```

## 4. Try it

```
lumadeck new sunset_clock --screen round_360 --theme sunset --widget clock
```

## Tips

* All color values are quoted `"0xRRGGBB"` strings.
* You can change the font family per theme by setting `font_family:`.
* Increase `border_w` and `radius_md` for a chunkier look.
* `anim_time` controls page-transition speed everywhere via
  `packages/nav.yaml`.
