# Verifying examples with ESPHome

The CLI in `tools/lumadeck/` validates files against the LumaDeck
contracts (theme keys, layout pages, widget headers). It does **not**
know whether the LVGL YAML inside a widget is something ESPHome will
actually accept. For that we run ESPHome's own validator:

```
esphome config <path/to/example.yaml>
```

This is the **P0 task** in [`../todo.md`](../todo.md). Until every
example passes `esphome config`, every widget is built on assumption.

## What `esphome config` does

`esphome config` loads the YAML, expands `!include`/`!extend`/
`!secret`, resolves all substitutions, and validates the merged
document against ESPHome's component schemas. It prints the fully
expanded YAML on success and a parse / schema error on failure.

It does **not** compile firmware (that's `esphome compile`). So this
step is fast and doesn't need a board attached.

## One-time setup

ESPHome is heavy (~200 MB, pulls in platformio). It's behind an opt-in
extras group so the default dev install stays light.

### Option A — pip (recommended)

```bash
make install-verify
# or, equivalently:
pip install -e .[verify]
```

### Option B — pipenv

```bash
pipenv install --dev   # Pipfile already lists esphome under dev-packages
```

### Option C — the standard ESPHome install

If you already have ESPHome installed via the
[official install steps](https://esphome.io/guides/installing_esphome.html),
nothing else to do. `make verify` just shells out to whatever
`esphome` is on PATH.

### Verify it landed

```bash
esphome version
```

You should see something like `Version: 2024.x.y`.

## Run the verification

From the repo root:

```bash
make verify
```

This runs `esphome config` against every **device** example in
`examples/` and reports a pass / skip / fail count at the end.

### Device vs package-preview examples

The verifier categorises files into two buckets based on whether
they define a top-level `display:` block:

* **DEVICE** — has a `display:` block. Validated. Today only
  `examples/lilygo-t-display-amoled.yaml` falls here.
* **PREVIEW** — no `display:` block. *Skipped*, not failed. These
  are LumaDeck-package previews (`media-remote.yaml`,
  `room-controller.yaml`, etc.) that show how to wire packages
  together but rely on a consumer-supplied driver block to actually
  compile.

The implementation lives in
[`tools/verify_examples.py`](../tools/verify_examples.py) and is
intentionally short — a few dozen lines of Python.

To check a single file:

```bash
esphome config examples/round-clock.yaml
```

### About `examples/secrets.yaml`

ESPHome resolves `!secret wifi_ssid` etc. by looking for a
`secrets.yaml` next to the file being processed. To keep `make verify`
zero-touch:

* `examples/secrets.example.yaml` is **committed**. It contains
  obvious placeholder strings — they're safe to commit and exist
  purely to let `esphome config` resolve secrets during validation.
* `examples/secrets.yaml` is **gitignored**. `make verify` copies the
  template to this path on first run so ESPHome can find it.

These placeholders are **not valid for actually flashing hardware**.
For a real build, copy `secrets.example.yaml` into your consumer repo
(or use the template at `consumer-repo-template/secrets.example.yaml`)
and fill in your real wifi credentials there.

## What success looks like

```
== examples/round-clock.yaml ==
INFO Reading configuration examples/round-clock.yaml...
substitutions:
  device_name: round_clock
  ...
esphome:
  name: round_clock
  ...
lvgl:
  ...
```

A long stretch of expanded YAML and **no `ERROR`** lines = pass.

## What failure looks like

```
== examples/round-clock.yaml ==
INFO Reading configuration examples/round-clock.yaml...
ERROR Error while reading config: Invalid YAML syntax:

while parsing a block mapping
expected <block end>, but found '<scalar>'
  in "examples/round-clock.yaml", line 23, column 5
```

or:

```
ERROR [lvgl.pages.0.widgets.2] Cannot find component 'foo'
```

Three failure modes I expect to see, ranked by likelihood:

1. **`!extend` on LVGL pages isn't supported.** I assumed ESPHome can
   merge a widget's `lvgl.pages: - id: !extend home_page` block into
   the layout's `lvgl.pages: - id: home_page`. If that's wrong, the
   fix is to either:
   * compose widgets directly inside layout files (the
     `widgets/home_dashboard.yaml` pattern), or
   * have widgets export `top_layer:` overlays / standalone pages
     instead of mutating existing ones.
2. **A widget property name is off.** ESPHome's LVGL component renames
   things from raw LVGL (`text_color` vs `text_color`, `align_to.id`
   vs `align_to`). Easy fixes once we see the schema error.
3. **A `lvgl.label.update` or similar action signature changed.**
   Same — schema error will tell us the right arg name.

## Reporting back

If a file fails, open an issue (or paste the output back to whoever's
helping) with:

* Which example file
* Your `esphome version`
* The full error block (from `INFO Reading configuration` to the
  blank line after the error)

That's enough to fix the widget without further round trips.

## CI vs local

The `validate` job in `.github/workflows/ci.yml` runs `lumadeck
validate-all` and `pytest` on every PR — fast, no ESPHome needed.

A second `esphome-config` job runs `esphome config` against every
example with `|| true` so failures don't block PRs yet. Once all
examples pass locally, drop the `|| true` to make this strict.
