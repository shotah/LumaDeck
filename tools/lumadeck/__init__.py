"""LumaDeck CLI package.

A small toolkit for scaffolding consumer device YAML files and
validating themes/layouts/widgets against the LumaDeck contracts
(see docs/theme-contract.md, docs/layout-contract.md,
docs/widget-contract.md).
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lumadeck")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
