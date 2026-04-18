"""Smoke tests for the LumaDeck validators."""

from __future__ import annotations

from pathlib import Path

import pytest

from lumadeck.validate import (
    validate_layout,
    validate_path,
    validate_theme,
    validate_widget,
)

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "rel",
    sorted(p.relative_to(REPO).as_posix() for p in (REPO / "themes").glob("*.yaml")),
)
def test_themes_pass_contract(rel: str) -> None:
    result = validate_theme(REPO / rel)
    assert result.ok, result.render()


@pytest.mark.parametrize(
    "rel",
    sorted(p.relative_to(REPO).as_posix() for p in (REPO / "layouts").glob("*.yaml")),
)
def test_layouts_pass_contract(rel: str) -> None:
    result = validate_layout(REPO / rel)
    assert result.ok, result.render()


@pytest.mark.parametrize(
    "rel",
    sorted(
        p.relative_to(REPO).as_posix()
        for p in (REPO / "widgets").glob("*.yaml")
        if not p.stem.startswith("_")
    ),
)
def test_widgets_pass_contract(rel: str) -> None:
    result = validate_widget(REPO / rel)
    assert result.ok, result.render()
    assert not result.warnings, result.render()


def test_validate_path_dispatches_correctly() -> None:
    assert validate_path(REPO / "themes" / "dark.yaml").ok
    assert validate_path(REPO / "layouts" / "round_360.yaml").ok
    assert validate_path(REPO / "widgets" / "clock.yaml").ok
