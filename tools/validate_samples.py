#!/usr/bin/env python3
"""
Validate JSON sample files for structure and basic expectations.

- Ensures each .json file under samples/ parses successfully.
- Optionally enforces that the root is a list or dict (current repo uses list).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"


def validate_json_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:  # pragma: no cover - CI feedback
        raise ValueError(f"{path}: JSON parse error at line {exc.lineno} column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, (list, dict)):
        raise ValueError(f"{path}: Expected root JSON array or object.")


def main() -> int:
    json_files = sorted(SAMPLES_DIR.glob("*.json"))
    errors: list[str] = []
    for path in json_files:
        try:
            validate_json_file(path)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        print("Sample validation failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"Validated {len(json_files)} sample JSON files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

