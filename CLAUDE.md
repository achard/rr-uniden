# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**rr-uniden** is a Python library for parsing and manipulating Uniden radio scanner configuration files (`.hpd` format). It also includes utilities for RadioReference trunked channel data. Standard library only — no external runtime dependencies.

Requires **Python 3.10+** (uses `match`/`case` statements and `X | Y` union type syntax).

## Commands

```bash
# Lint (two-pass, matching CI)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Test
pytest

# Run a single test
pytest test_objects.py::test_function_name
```

Dev dependencies: `pip install flake8 pytest`

## Architecture

The codebase models a Uniden `.hpd` config file as a hierarchy of dataclasses:

```
UnidenFile
 └─ System (TrunkedSystem | ConventionalSystem)
     ├─ Radio (UID entries)
     ├─ TrunkedGroup / ConventionalGroup
     │   └─ TrunkedChannel / ConventionalFrequency
     └─ Site (trunked only)
         └─ SiteFrequency
```

### Serialization Protocol

Every domain object implements a consistent interface:
- **`from_text(cls, text)`** — parse a single tab-delimited line from an `.hpd` file
- **`export()`** — serialize back to tab-delimited format
- **`from_file(cls, file)`** — recursive parsing from a file stream, using `file.tell()`/`file.seek()` for backtracking when a line doesn't belong to the current object

### Key Files

- `uniden/objects.py` — All domain objects (UnidenFile, System, Group, Channel, Site, etc.)
- `uniden/base_classes.py` — Value types: `UnidenBool` ("On"/"Off"), `UnidenRange`, `AlertTone`, `AlertLight`, `ServiceType` (bidirectional index↔name mapping), `UnidenTextType` (abstract base)
- `radioreference/__Init__.py` — `TrunkedChannel` and `TrunkedChannelDict` for RadioReference CSV data

### Dispatch Pattern

Line prefixes in `.hpd` files identify object types. Parsing uses `match`/`case` on `line.split("\t")[0]` to dispatch to the correct class's `from_text()`. Each `from_file()` reads lines until it encounters an unrecognized prefix, then seeks back so the parent parser can handle it.
