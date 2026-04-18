# Contributing to LumaDeck

Thanks for considering a contribution! LumaDeck is built around three
small contracts — keep your change inside the right one and you'll
have a smooth time.

## Quick start

```bash
git clone https://github.com/shotah/LumaDeck
cd LumaDeck
make install-dev   # or: pip install -e .[dev]
make check         # runs lint + validate + test
```

Don't have `make`? Use `pipenv install --dev` (the `Pipfile` mirrors
`pyproject.toml`) or run the raw commands: `yamllint .`,
`lumadeck validate-all`, `pytest`.

### Verifying the YAML compiles in ESPHome

The `check` gates above only enforce LumaDeck's contracts — they don't
ask ESPHome whether the LVGL YAML is actually valid. To do that:

```bash
make install-verify   # adds ESPHome (~200MB; heavy but only once)
make verify           # runs `esphome config` against every example
```

Full walkthrough (including expected output, common failure modes, and
how to report issues) lives in
[`docs/verifying-examples.md`](./docs/verifying-examples.md). If
you're touching widgets, **please run `make verify` before opening a
PR** — that's the only thing that catches LVGL schema mistakes my
contract validator can't see.

## Where does my change go?

| You want to...                              | Add files to | Read first |
| ------------------------------------------- | ------------ | ---------- |
| Add a color/font scheme                     | `themes/`    | [`docs/authoring-a-theme.md`](./docs/authoring-a-theme.md) |
| Support a new screen size or shape          | `layouts/`   | [`docs/authoring-a-layout.md`](./docs/authoring-a-layout.md) |
| Add a UI component                          | `widgets/`   | [`docs/authoring-a-widget.md`](./docs/authoring-a-widget.md) |
| Add a new ESP variant or HA helper          | `packages/`  | [`docs/architecture.md`](./docs/architecture.md) |
| Improve the CLI                             | `tools/lumadeck/` | source comments |

## The contracts

Every theme/layout/widget is checked by `lumadeck validate-all` (and
the CI workflow). The contracts are documented at:

* [`docs/theme-contract.md`](./docs/theme-contract.md)
* [`docs/layout-contract.md`](./docs/layout-contract.md)
* [`docs/widget-contract.md`](./docs/widget-contract.md)

Don't break them. If your change requires a contract change, open an
issue first — that's a major version bump.

## Style guide

* YAML: 2-space indent, no tabs, LF line endings, max line length 120.
  Enforced by `.yamllint.yaml`.
* Python: type-hinted, formatted with `black` (default settings),
  `from __future__ import annotations` at the top of every module.
* All ids in widgets are prefixed `lum_<widget_name>_`.
* All color values are quoted `"0xRRGGBB"` strings.
* All comments explain *why*, not *what*. The code already says what.

## Pull request checklist

* [ ] `make check` passes (or, equivalently, `pytest` +
      `lumadeck validate-all` + `yamllint .`)
* [ ] If you added a widget/theme/layout, you also added an entry to
      its contract docs and (where relevant) `docs/screen-sizes.md`.
* [ ] If you added a widget, you wired it into at least one example
      under `examples/` so future contributors see real usage.
* [ ] You bumped `CHANGELOG.md` under `[Unreleased]`.

## Commit messages

Short imperative subject, ~72 chars. Body if it needs context.
Reference issues with `#NNN`.

```
add ring_slider widget for brightness/volume

Anchors to home_page, posts to light.turn_on by default.
Configurable via ${ring_target_entity} and ${ring_service}.
Closes #42.
```

## License

By contributing you agree your work is published under the same MIT
license as the rest of the project.
