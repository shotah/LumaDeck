# Touch gestures

LumaDeck implements **software swipe detection** in
`packages/touch.yaml` so any touchscreen driver gets multi-page
navigation for free. The driver itself stays in your consumer device
YAML (it's hardware-specific); the package supplies the gesture logic
on top.

Out of the box:

* **Swipe left**  → `nav_next_page`
* **Swipe right** → `nav_prev_page`

Vertical swipes are reserved for v0.3 (pull-to-refresh, dismiss
toast, etc.).

## How it works

`packages/touch.yaml` defines six globals (start x/y/ms,
last x/y, active flag) and three scripts:

| Script              | Called from              | Job                                  |
| ------------------- | ------------------------ | ------------------------------------ |
| `lum_touch_press`   | `touchscreen.on_touch:`  | Records the gesture origin           |
| `lum_touch_update`  | `touchscreen.on_update:` | Tracks the latest touch coordinate   |
| `lum_touch_release` | `touchscreen.on_release:`| Computes Δx/Δy/Δt and dispatches a swipe |

A swipe qualifies if:

* Total time < `${swipe_max_time_ms}` (default `500` ms)
* Horizontal distance > `${swipe_min_dist}` (default `60` px)
* Horizontal distance > vertical distance (so vertical drags don't fire)

## Wiring (consumer device YAML)

Paste this into the `touchscreen:` block of your device YAML —
exactly the same regardless of which touch IC you're using.

```yaml
touchscreen:
  - platform: <your_touch_ic>     # cst816, gt911, ft6336, ...
    id: lum_touchscreen
    # ... driver-specific config (i2c_id, interrupt_pin, etc.) ...

    on_touch:
      - script.execute:
          id: lum_touch_press
          x: !lambda 'return touch.x;'
          y: !lambda 'return touch.y;'

    on_update:
      - if:
          condition:
            lambda: 'return !touches.empty();'
          then:
            - script.execute:
                id: lum_touch_update
                x: !lambda 'return touches[0].x;'
                y: !lambda 'return touches[0].y;'

    on_release:
      - script.execute: lum_touch_release
```

`examples/lilygo-t-display-amoled.yaml` and
`consumer-repo-template/device.yaml` already do this — they're the
shortest reference.

## Tuning

Override the substitutions in your device YAML, **above** the
`packages:` block:

```yaml
substitutions:
  swipe_min_dist:    "80"   # demand a longer swipe (less sensitive)
  swipe_max_time_ms: "350"  # require a snappier flick
```

A higher `swipe_min_dist` makes accidental swipes during slider /
arc drags less likely; a lower one makes navigation feel snappier.
For 240 px-wide screens, 50–80 px is the useful range.

## Known limitations

* **Slider/arc drag conflict.** ESPHome's touchscreen events fire
  alongside LVGL widget interaction, so a long horizontal slider
  drag can also be detected as a swipe. The high default threshold
  mitigates this. A v0.3 follow-up will add edge-only swipes (only
  swipes starting in `region_left` / `region_right` count as
  navigation), which sidesteps the issue entirely.
* **CST816 native gestures.** The CST816 IC can report gestures
  itself, but exposing that is driver-specific. Software detection
  works for every touchscreen LumaDeck supports, so we lean on it
  for now.

## Disabling

If you don't want swipe navigation on a given device, just don't
wire `on_release: lum_touch_release` in the touchscreen block. The
press / update tracking is harmless without it (other widgets may
read `lum_touch_active` as an idle indicator).
