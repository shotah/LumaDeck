"""Thin shim that defers to the lumadeck CLI.

Kept for backwards compatibility with the original v0.1 stub. Prefer
running `lumadeck` directly after `pip install -e .` from the repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from lumadeck.cli import cli

if __name__ == "__main__":
    cli()
