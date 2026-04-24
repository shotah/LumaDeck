"""Command-line entry point for LumaDeck tooling.

Usage examples:

    lumadeck list themes
    lumadeck new desk_panel --screen round_360 --theme dark \
        --widget clock --widget nav_tabs
    lumadeck validate themes/dark.yaml
    lumadeck validate-all
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .generate import REPO_ROOT, available, generate
from .validate import (
    collect_nav_page_refs,
    validate_layout_against_nav,
    validate_path,
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="lumadeck")
def cli() -> None:
    """LumaDeck — universal ESPHome + LVGL UI package toolkit."""


@cli.command("list")
@click.argument("kind", type=click.Choice(["themes", "layouts", "widgets"]))
def list_kind(kind: str) -> None:
    """List available themes / layouts / widgets."""

    items = available(kind)
    if not items:
        click.echo(f"(no {kind} found)")
        return
    for item in items:
        click.echo(item)


@cli.command("new")
@click.argument("name")
@click.option("--screen", required=True, help="layout name (e.g. round_360)")
@click.option("--theme", default="dark", show_default=True)
@click.option(
    "--widget",
    "widgets",
    multiple=True,
    help="widget to include (repeatable)",
)
@click.option("--board", default="esp32s3", show_default=True)
@click.option("--no-ha", is_flag=True, help="omit packages/ha.yaml")
@click.option("--no-nav", is_flag=True, help="omit packages/nav.yaml")
@click.option(
    "--out-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="directory to write into (defaults to examples/)",
)
def new_device(
    name: str,
    screen: str,
    theme: str,
    widgets: tuple[str, ...],
    board: str,
    no_ha: bool,
    no_nav: bool,
    out_dir: Path | None,
) -> None:
    """Scaffold a new device YAML."""

    try:
        path = generate(
            name=name,
            screen=screen,
            theme=theme,
            widgets=list(widgets) or ["clock"],
            board=board,
            include_ha=not no_ha,
            include_nav=not no_nav,
            out_dir=out_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"wrote {path}")


@cli.command("validate")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def validate(paths: tuple[Path, ...]) -> None:
    """Validate one or more theme / layout / widget files."""

    if not paths:
        raise click.UsageError("provide at least one file path")
    failures = 0
    for path in paths:
        result = validate_path(path)
        click.echo(result.render())
        if not result.ok:
            failures += 1
    if failures:
        sys.exit(1)


@cli.command("validate-all")
def validate_all() -> None:
    """Validate every file under themes/, layouts/, widgets/."""

    failures = 0

    # Cross-check: every page id referenced by packages/nav.yaml must
    # exist in every layout. Catches the class of bug where adding
    # `nav_goto_<page>` to nav.yaml without updating layouts crashes
    # consumers at config time.
    nav_refs = collect_nav_page_refs(REPO_ROOT / "packages" / "nav.yaml")
    if nav_refs:
        click.echo(
            "== nav <-> layout cross-check =="
            f" (nav.yaml references: {sorted(nav_refs)})"
        )
        for layout in sorted((REPO_ROOT / "layouts").glob("*.yaml")):
            if layout.stem.startswith("_"):
                continue
            result = validate_layout_against_nav(layout, nav_refs)
            if not result.ok:
                click.echo(result.render())
                failures += 1

    for kind in ("themes", "layouts", "widgets"):
        folder = REPO_ROOT / kind
        for path in sorted(folder.glob("*.yaml")):
            if path.stem.startswith("_"):
                continue
            result = validate_path(path)
            click.echo(result.render())
            if not result.ok:
                failures += 1
    if failures:
        click.echo(f"\n{failures} file(s) failed validation", err=True)
        sys.exit(1)
    click.echo("\nall good")


if __name__ == "__main__":
    cli()
