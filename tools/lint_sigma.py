#!/usr/bin/env python3
"""
Basic Sigma validation for repo hunts.

Checks each *.sigma.yaml file under hunts/ to ensure:
- Required high-level keys exist.
- Either a detection block with a condition is present or a sequence is defined.
- Each detection/sequence entry contains a logsource definition.

Requires PyYAML (installed in CI workflow).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
HUNTS_DIR = REPO_ROOT / "hunts"


class ValidationError(Exception):
    pass


def validate_sigma_file(path: Path) -> None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - CI feedback
        raise ValidationError(f"{path}: YAML parsing error: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{path}: Expected mapping at top level.")

    required_keys = {"title", "id", "status", "level"}
    missing = sorted(required_keys - data.keys())
    if missing:
        raise ValidationError(f"{path}: Missing required keys: {', '.join(missing)}")

    if "type" in data and data["type"] != "sequence":
        raise ValidationError(f"{path}: Unsupported type '{data['type']}' (expected 'sequence' or omitted).")

    if "sequence" in data:
        if not isinstance(data["sequence"], list) or not data["sequence"]:
            raise ValidationError(f"{path}: 'sequence' must be a non-empty list.")
        for idx, stage in enumerate(data["sequence"]):
            if not isinstance(stage, dict):
                raise ValidationError(f"{path}: sequence[{idx}] must be a mapping.")
            if "logsource" not in stage:
                raise ValidationError(f"{path}: sequence[{idx}] missing 'logsource'.")
            if "detection" not in stage:
                raise ValidationError(f"{path}: sequence[{idx}] missing 'detection'.")
            if "condition" not in stage["detection"]:
                raise ValidationError(f"{path}: sequence[{idx}] detection missing 'condition'.")
    else:
        if "logsource" not in data:
            raise ValidationError(f"{path}: Missing 'logsource'.")
        if "detection" not in data:
            raise ValidationError(f"{path}: Missing 'detection'.")
        detection = data["detection"]
        if not isinstance(detection, dict) or "condition" not in detection:
            raise ValidationError(f"{path}: detection block must include 'condition'.")

    if "tags" not in data or not data["tags"]:
        raise ValidationError(f"{path}: Include at least one ATT&CK tag under 'tags'.")


def main() -> int:
    sigma_files = sorted(HUNTS_DIR.glob("*.sigma.yaml"))
    errors: list[str] = []
    for path in sigma_files:
        try:
            validate_sigma_file(path)
        except ValidationError as exc:
            errors.append(str(exc))
    if errors:
        print("Sigma validation failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"Validated {len(sigma_files)} Sigma files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

