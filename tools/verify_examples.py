"""Run `esphome config` against every example device YAML.

Used by `make verify` and the Pipenv `verify` script.

Categorises files into three buckets:

* DEVICE   — has a top-level `display:` block; gets validated.
* PREVIEW  — no `display:` block; skipped with an explanatory note.
             These are LumaDeck-package previews (e.g.
             `media-remote.yaml`, `room-controller.yaml`) that need a
             consumer-supplied driver block to actually compile.
* SECRETS  — `secrets*.yaml`; never validated.

Exits 0 if every DEVICE-category file passed, 1 otherwise.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "examples"
SECRETS_TEMPLATE = EXAMPLES / "secrets.example.yaml"
SECRETS_TARGET = EXAMPLES / "secrets.yaml"

_DISPLAY_BLOCK_RE = re.compile(r"^display:\s*$", re.MULTILINE)


def _is_device_yaml(path: Path) -> bool:
    """A device YAML is one that defines its own `display:` block."""

    text = path.read_text(encoding="utf-8")
    return bool(_DISPLAY_BLOCK_RE.search(text))


def _bootstrap_secrets() -> None:
    if SECRETS_TARGET.exists():
        return
    if not SECRETS_TEMPLATE.exists():
        print(f"WARN: {SECRETS_TEMPLATE} missing; cannot bootstrap secrets")
        return
    shutil.copyfile(SECRETS_TEMPLATE, SECRETS_TARGET)
    print(f"created {SECRETS_TARGET.relative_to(REPO_ROOT)} from template")


def main() -> int:
    _bootstrap_secrets()

    files = sorted(EXAMPLES.glob("*.yaml"))
    fails: list[Path] = []
    skipped: list[Path] = []
    passed: list[Path] = []

    for path in files:
        if "secrets" in path.name:
            continue

        rel = path.relative_to(REPO_ROOT).as_posix()

        if not _is_device_yaml(path):
            print(f"\n== {rel}  [SKIP — no display: block, package preview only]")
            skipped.append(path)
            continue

        print(f"\n== {rel}  [DEVICE]")
        rc = subprocess.call(["esphome", "config", str(path)])
        if rc != 0:
            fails.append(path)
        else:
            passed.append(path)

    print("\n" + "=" * 60)
    print(f"  passed:  {len(passed)}")
    print(f"  skipped: {len(skipped)}  (package previews — no display block)")
    print(f"  failed:  {len(fails)}")
    if fails:
        print("\nfailed files:")
        for f in fails:
            print(f"  - {f.relative_to(REPO_ROOT).as_posix()}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
