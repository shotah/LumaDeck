"""Smoke tests for the device-YAML scaffolder."""

from __future__ import annotations

from pathlib import Path

import pytest

from lumadeck.generate import available, generate


def test_available_lists_are_nonempty() -> None:
    assert "dark" in available("themes")
    assert "round_360" in available("layouts")
    assert "clock" in available("widgets")


def test_generate_writes_a_consumable_file(tmp_path: Path) -> None:
    out = generate(
        name="unit_test_device",
        screen="round_360",
        theme="dark",
        widgets=["clock", "nav_tabs"],
        out_dir=tmp_path,
    )
    text = out.read_text(encoding="utf-8")
    assert "device_name" in text
    assert "../themes/dark.yaml" in text
    assert "../layouts/round_360.yaml" in text
    assert "../widgets/clock.yaml" in text
    assert "../widgets/nav_tabs.yaml" in text


def test_generate_rejects_unknown_layout(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown layout"):
        generate(
            name="bad",
            screen="not_a_real_layout",
            theme="dark",
            widgets=["clock"],
            out_dir=tmp_path,
        )


def test_generate_rejects_unknown_widget(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown widget"):
        generate(
            name="bad",
            screen="round_360",
            theme="dark",
            widgets=["clock", "nope"],
            out_dir=tmp_path,
        )
