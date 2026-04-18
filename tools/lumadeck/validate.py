"""Validate themes / layouts / widgets against the LumaDeck contracts."""

from __future__ import annotations

import re
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.constructor import SafeConstructor

from .contract import (
    LAYOUT_REQUIRED_KEYS,
    LAYOUT_REQUIRED_PAGES,
    LAYOUT_VALID_SHAPES,
    THEME_COLOR_KEYS,
    THEME_REQUIRED_KEYS,
    WIDGET_HEADER_REQUIRED_FIELDS,
    WIDGET_ID_PREFIX,
    ValidationResult,
)

_HEX_COLOR_RE = re.compile(r"^0x[0-9A-Fa-f]{6}$")
_HEADER_FIELD_RE = re.compile(r"^#\s*([a-z_]+)\s*:\s*(.+?)\s*$")

# ESPHome uses several custom YAML tags. Register them as opaque
# pass-throughs so we can still walk the document structure.
_ESPHOME_TAGS: tuple[str, ...] = (
    "!extend",
    "!lambda",
    "!secret",
    "!include",
    "!include_dir_list",
    "!include_dir_merge_list",
    "!include_dir_named",
    "!include_dir_merge_named",
)


def _passthrough(loader, node):
    if hasattr(node, "value"):
        return node.value
    return None


def _build_yaml() -> YAML:
    yaml = YAML(typ="safe")
    for tag in _ESPHOME_TAGS:
        yaml.constructor.add_constructor(tag, _passthrough)
        SafeConstructor.add_constructor(tag, _passthrough)
    return yaml


_yaml = _build_yaml()


def _load(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    try:
        data = _yaml.load(text)
    except Exception as exc:
        raise ValueError(f"YAML parse error: {exc}") from exc
    return data if isinstance(data, dict) else None


def validate_theme(path: Path) -> ValidationResult:
    """Validate a theme YAML against `docs/theme-contract.md`."""

    result = ValidationResult(path=str(path))
    try:
        data = _load(path)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    if not data or "substitutions" not in data:
        result.errors.append("missing top-level 'substitutions:' block")
        return result

    subs = data["substitutions"] or {}

    for key in THEME_REQUIRED_KEYS:
        if key not in subs:
            result.errors.append(f"missing required key: {key}")

    for key, value in subs.items():
        if key in THEME_COLOR_KEYS:
            if not isinstance(value, str) or not _HEX_COLOR_RE.match(value):
                result.errors.append(
                    f"{key!r} must be a quoted '0xRRGGBB' string, got {value!r}"
                )

    return result


def validate_layout(path: Path) -> ValidationResult:
    """Validate a layout YAML against `docs/layout-contract.md`."""

    result = ValidationResult(path=str(path))
    try:
        data = _load(path)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    if not data:
        result.errors.append("empty layout file")
        return result

    subs = data.get("substitutions") or {}
    for key in LAYOUT_REQUIRED_KEYS:
        if key not in subs:
            result.errors.append(f"missing required substitution: {key}")

    shape = subs.get("screen_shape")
    if shape and shape not in LAYOUT_VALID_SHAPES:
        result.errors.append(
            f"screen_shape must be one of {sorted(LAYOUT_VALID_SHAPES)}, got {shape!r}"
        )

    lvgl = data.get("lvgl") or {}
    pages = lvgl.get("pages") or []
    page_ids = {p.get("id") for p in pages if isinstance(p, dict)}
    for required in LAYOUT_REQUIRED_PAGES:
        if required not in page_ids:
            result.errors.append(f"layout must define page id: {required}")

    return result


def validate_widget(path: Path) -> ValidationResult:
    """Validate a widget YAML against `docs/widget-contract.md`."""

    result = ValidationResult(path=str(path))
    text = path.read_text(encoding="utf-8")

    header_fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            if header_fields:
                break
            continue
        m = _HEADER_FIELD_RE.match(stripped)
        if m:
            header_fields[m.group(1)] = m.group(2)

    for field_name in WIDGET_HEADER_REQUIRED_FIELDS:
        if field_name not in header_fields:
            result.errors.append(
                f"widget header is missing '# {field_name}: ...' line"
            )

    try:
        data = _load(path)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    for found_id in _walk_ids(data):
        if not found_id.startswith(WIDGET_ID_PREFIX) and found_id not in {
            "home_page",
            "media_page",
            "lights_page",
            "climate_page",
            "settings_page",
            "ha_time",
            "region_top",
            "region_center",
            "region_bottom",
            "region_left",
            "region_right",
        }:
            result.warnings.append(
                f"id {found_id!r} doesn't start with '{WIDGET_ID_PREFIX}' "
                "and isn't a known page id"
            )

    return result


def _walk_ids(node: object) -> list[str]:
    """Yield every value under any 'id:' key found in nested dicts/lists."""

    found: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "id" and isinstance(v, str):
                found.append(v)
            else:
                found.extend(_walk_ids(v))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_ids(item))
    return found


def validate_path(path: Path) -> ValidationResult:
    """Pick the right validator based on the file's parent directory."""

    parent = path.parent.name
    if parent == "themes":
        return validate_theme(path)
    if parent == "layouts":
        return validate_layout(path)
    if parent == "widgets":
        return validate_widget(path)
    result = ValidationResult(path=str(path))
    result.warnings.append(
        f"don't know how to validate files under {parent!r}; skipped"
    )
    return result
