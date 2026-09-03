#!/usr/bin/env python3
"""Validate the bundled Jennie look corpus and print coverage statistics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


REQUIRED = {
    "id",
    "date",
    "scene",
    "title",
    "source_ids",
    "evidence_tier",
    "observed_items",
    "silhouette",
    "palette",
    "textures",
    "proportion_devices",
    "accessories",
    "beauty",
    "styling_devices",
    "ordinary_translation",
    "confidence",
}
ALLOWED_SCENES = {"airport", "off-duty", "stage", "formal-event"}
ALLOWED_TIERS = {"A", "B", "C"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
LIST_FIELDS = {
    "source_ids",
    "observed_items",
    "silhouette",
    "palette",
    "textures",
    "proportion_devices",
    "accessories",
    "beauty",
    "styling_devices",
}
START = date(2024, 9, 1)
END = date(2026, 8, 31)


def validate(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    ids: set[str] = set()

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"cannot read {path}: {exc}"]

    for line_no, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue

        missing = sorted(REQUIRED - item.keys())
        if missing:
            errors.append(f"line {line_no}: missing fields: {', '.join(missing)}")

        record_id = item.get("id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"line {line_no}: id must be a non-empty string")
        elif record_id in ids:
            errors.append(f"line {line_no}: duplicate id {record_id}")
        else:
            ids.add(record_id)

        try:
            raw_date = item.get("date", "")
            # Preserve YYYY-MM when the exact day has not been verified. Only
            # range validation normalizes it to the first day of that month.
            normalized_date = f"{raw_date}-01" if re.fullmatch(r"\d{4}-\d{2}", raw_date) else raw_date
            look_date = date.fromisoformat(normalized_date)
            if not START <= look_date <= END:
                errors.append(f"line {line_no}: date {look_date} outside {START}..{END}")
        except (TypeError, ValueError):
            errors.append(f"line {line_no}: date must use ISO YYYY-MM or YYYY-MM-DD")

        if item.get("scene") not in ALLOWED_SCENES:
            errors.append(f"line {line_no}: invalid scene {item.get('scene')!r}")
        if item.get("evidence_tier") not in ALLOWED_TIERS:
            errors.append(f"line {line_no}: invalid evidence_tier {item.get('evidence_tier')!r}")
        if item.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"line {line_no}: invalid confidence {item.get('confidence')!r}")

        for field in LIST_FIELDS:
            value = item.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
                errors.append(f"line {line_no}: {field} must be a non-empty string array")

        if not isinstance(item.get("ordinary_translation"), str) or not item.get("ordinary_translation"):
            errors.append(f"line {line_no}: ordinary_translation must be non-empty")

        records.append(item)

    sources_path = path.with_name("sources.md")
    try:
        source_text = sources_path.read_text(encoding="utf-8")
        registered_sources = set(re.findall(r"^- `([A-Z]\d{2})`", source_text, re.MULTILINE))
        if not registered_sources:
            errors.append(f"no source IDs found in {sources_path}")
        for item in records:
            unknown = sorted(set(item.get("source_ids", [])) - registered_sources)
            if unknown:
                errors.append(f"record {item.get('id')}: unregistered source IDs: {', '.join(unknown)}")
    except OSError as exc:
        errors.append(f"cannot read source registry {sources_path}: {exc}")

    return records, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path, help="Path to look-corpus.jsonl")
    args = parser.parse_args()

    records, errors = validate(args.corpus)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    scenes = Counter(record["scene"] for record in records)
    tiers = Counter(record["evidence_tier"] for record in records)
    print(f"Validated {len(records)} unique looks")
    print("Scenes: " + ", ".join(f"{key}={scenes[key]}" for key in sorted(scenes)))
    print("Evidence tiers: " + ", ".join(f"{key}={tiers[key]}" for key in sorted(tiers)))

    combined_everyday = scenes["airport"] + scenes["off-duty"]
    coverage = {
        "airport/off-duty combined": combined_everyday,
        "stage": scenes["stage"],
        "formal-event": scenes["formal-event"],
    }
    weak = [f"{name}={count}" for name, count in coverage.items() if count < 5]
    if weak:
        print("ERROR: insufficient main-scene coverage: " + ", ".join(weak), file=sys.stderr)
        return 1
    print("Coverage threshold met: at least 5 looks per main scene group")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
