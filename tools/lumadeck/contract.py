"""Machine-readable LumaDeck contracts.

Kept in code (not YAML) so validation runs without parsing a separate
spec. Mirrors the docs in `docs/*-contract.md` — keep them in sync.
"""

from __future__ import annotations

from dataclasses import dataclass, field

THEME_REQUIRED_KEYS: tuple[str, ...] = (
    "bg",
    "bg_alt",
    "fg",
    "fg_muted",
    "accent",
    "accent_alt",
    "success",
    "warn",
    "error",
    "border",
    "font_family",
    "font_size_xl",
    "font_size_lg",
    "font_size_md",
    "font_size_sm",
    "font_size_icon",
    "radius_sm",
    "radius_md",
    "radius_lg",
    "radius_pill",
    "pad_sm",
    "pad_md",
    "pad_lg",
    "border_w",
)

THEME_COLOR_KEYS: frozenset[str] = frozenset(
    {
        "bg",
        "bg_alt",
        "fg",
        "fg_muted",
        "accent",
        "accent_alt",
        "success",
        "warn",
        "error",
        "border",
        "gradient_a",
        "gradient_b",
        "shadow_color",
    }
)

LAYOUT_REQUIRED_KEYS: tuple[str, ...] = (
    "screen_w",
    "screen_h",
    "screen_shape",
    "screen_radius",
    "scale",
)

LAYOUT_VALID_SHAPES: frozenset[str] = frozenset(
    {"round", "square", "wide", "tall"}
)

LAYOUT_REQUIRED_PAGES: tuple[str, ...] = (
    "home_page",
    "media_page",
    "lights_page",
    "climate_page",
    "settings_page",
)

WIDGET_HEADER_REQUIRED_FIELDS: tuple[str, ...] = (
    "widget",
    "version",
    "reads",
    "targets",
    "exposes",
)

WIDGET_ID_PREFIX: str = "lum_"


@dataclass
class ValidationResult:
    """Aggregated validation findings for a single file."""

    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        lines = [f"== {self.path} =="]
        if self.ok and not self.warnings:
            lines.append("  OK")
            return "\n".join(lines)
        for e in self.errors:
            lines.append(f"  ERROR  {e}")
        for w in self.warnings:
            lines.append(f"  WARN   {w}")
        return "\n".join(lines)
