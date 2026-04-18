# ---------------------------------------------------------------
# LumaDeck — project task runner.
#
# Every command the project knows about lives here. Run `make help`
# to see the catalogue. Targets are deliberately thin shell wrappers
# so newcomers can read the Makefile and learn the underlying tools
# (pip, pytest, yamllint, lumadeck CLI).
#
# Windows users: install GNU make via Chocolatey (`choco install make`),
# Scoop (`scoop install make`), or run from inside WSL.
# ---------------------------------------------------------------

# Use python -m to dodge PATH issues on fresh checkouts.
PY      ?= python
PIP     := $(PY) -m pip
PYTEST  := $(PY) -m pytest
YAMLLNT := $(PY) -m yamllint
LD      := lumadeck

# Default target prints help so `make` alone is always safe.
.DEFAULT_GOAL := help

# Mark every target as phony — none of them produce a file by their name.
.PHONY: help install install-dev install-verify install-all install-pipenv \
        test validate lint check ci verify \
        list-themes list-layouts list-widgets new \
        build publish-test clean

## help : Show this catalogue.
# Implemented in Python so it renders identically on Linux, macOS, and
# Windows (cmd.exe's `echo` doesn't strip surrounding quotes).
help:
	@$(PY) -c "print('''LumaDeck - make targets\n\n  Setup\n    install         Install runtime deps + the lumadeck CLI (editable)\n    install-dev     Install runtime + dev deps (pytest, yamllint)\n    install-verify  Install ESPHome so `make verify` works (heavy, ~200MB)\n    install-all     install-dev + install-verify\n    install-pipenv  Install via pipenv using Pipfile\n\n  Quality gates\n    test            Run the pytest suite\n    validate        Validate every theme/layout/widget against its contract\n    lint            Run yamllint across the repo\n    check           lint + validate + test (use this before pushing)\n    verify          Run `esphome config` against every examples/*.yaml\n                    (requires install-verify; see docs/verifying-examples.md)\n    ci              Same gates GitHub Actions runs\n\n  Discovery\n    list-themes     List built-in themes\n    list-layouts    List built-in layouts\n    list-widgets    List built-in widgets\n\n  Scaffolding\n    new NAME=foo SCREEN=round_360 THEME=dark WIDGETS=\"clock nav_tabs\"\n                    Generate a new device YAML in examples/\n\n  Packaging\n    build           Build the lumadeck Python package (wheel + sdist)\n    clean           Remove build artifacts and caches''')"

## install : Install runtime deps + the lumadeck CLI in editable mode.
install:
	$(PIP) install -e .

## install-dev : Install runtime + dev deps (pytest, yamllint).
install-dev:
	$(PIP) install -e .[dev]

## install-verify : Install ESPHome locally for `make verify`.
install-verify:
	$(PIP) install -e .[verify]

## install-all : install-dev + install-verify.
install-all:
	$(PIP) install -e .[dev,verify]

## install-pipenv : Install via pipenv using Pipfile.
install-pipenv:
	$(PIP) install --upgrade pipenv
	pipenv install --dev

## test : Run the pytest suite.
test:
	$(PYTEST) -q

## validate : Validate every theme/layout/widget against its contract.
validate:
	$(LD) validate-all

## lint : Run yamllint across the repo.
lint:
	$(YAMLLNT) .

## check : lint + validate + test. Run this before pushing.
check: lint validate test
	@$(PY) -c "print('\nall gates green')"

## ci : Same gates GitHub Actions runs.
ci: check

## verify : Run `esphome config` against every examples/*.yaml.
# Cross-shell loop in Python so it works the same on Windows / Linux /
# macOS. Requires `make install-verify` first. See
# docs/verifying-examples.md for what the output should look like.
verify:
	@$(PY) -c "import glob, subprocess, sys; \
files = sorted(glob.glob('examples/*.yaml')); \
fails = []; \
[print(f'\n== {f} ==') or (subprocess.call(['esphome', 'config', f]) and fails.append(f)) for f in files]; \
print(); \
print(f'{len(fails)} of {len(files)} example(s) failed: {fails}' if fails else f'all {len(files)} example(s) resolved'); \
sys.exit(1 if fails else 0)"

## list-themes : List built-in themes.
list-themes:
	$(LD) list themes

## list-layouts : List built-in layouts.
list-layouts:
	$(LD) list layouts

## list-widgets : List built-in widgets.
list-widgets:
	$(LD) list widgets

# Variables for the `new` target. Override on the command line:
#   make new NAME=desk SCREEN=round_360 THEME=dark WIDGETS='clock nav_tabs'
NAME    ?=
SCREEN  ?= round_360
THEME   ?= dark
WIDGETS ?= clock
BOARD   ?= esp32s3

## new : Scaffold a new device YAML. Requires NAME=...
new:
ifeq ($(strip $(NAME)),)
	@$(PY) -c "import sys; print('ERROR: NAME is required.'); print('  make new NAME=desk_panel SCREEN=round_360 THEME=dark WIDGETS=\"clock nav_tabs\"'); sys.exit(2)"
else
	$(LD) new $(NAME) --screen $(SCREEN) --theme $(THEME) --board $(BOARD) $(foreach w,$(WIDGETS),--widget $(w))
endif

## build : Build the lumadeck Python package (wheel + sdist).
build: clean
	$(PIP) install --upgrade build
	$(PY) -m build

## clean : Remove build artifacts and caches.
clean:
	@$(PY) -c "import shutil, pathlib; \
[shutil.rmtree(p, ignore_errors=True) for p in [ \
  'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache']]; \
[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; \
[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	@echo "cleaned"
