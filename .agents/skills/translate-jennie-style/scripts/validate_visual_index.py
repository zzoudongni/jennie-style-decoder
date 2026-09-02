#!/usr/bin/env python3
"""Validate remote visual references against the look corpus."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = {
    "visual_id",
    "look_id",
    "scene",
    "anchor_kind",
    "core_mechanism",
    "principles",
    "scenario_tags",
    "goal_tags",
    "fit_tags",
    "exposure_level",
    "transferability",
    "representativeness",
    "why_representative",
    "publisher",
    "source_page",
    "image_url",
    "alt",
    "checked_at",
    "use",
}


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
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
            errors.append(f"{path.name} line {line_no}: invalid JSON: {exc}")
            continue
        records.append(item)
    return records, errors


def is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("visual_index", type=Path)
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()

    visuals, errors = read_jsonl(args.visual_index)
    looks, corpus_errors = read_jsonl(args.corpus)
    errors.extend(corpus_errors)
    look_map = {item.get("id"): item for item in looks if item.get("id")}
    visual_ids = set()
    mechanisms = set()
    sources_path = args.visual_index.with_name("sources.md")
    try:
        source_registry = sources_path.read_text(encoding="utf-8")
    except OSError as exc:
        source_registry = ""
        errors.append(f"cannot read source registry {sources_path}: {exc}")

    for index, item in enumerate(visuals, 1):
        label = f"visual record {index}"
        missing = sorted(REQUIRED - item.keys())
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
        visual_id = item.get("visual_id")
        if not isinstance(visual_id, str) or not visual_id:
            errors.append(f"{label}: visual_id must be non-empty")
        elif visual_id in visual_ids:
            errors.append(f"{label}: duplicate visual_id {visual_id}")
        else:
            visual_ids.add(visual_id)

        mechanism = item.get("core_mechanism")
        if not isinstance(mechanism, str) or not mechanism:
            errors.append(f"{label}: core_mechanism must be non-empty")
        elif mechanism in mechanisms:
            errors.append(f"{label}: duplicate core_mechanism {mechanism}")
        else:
            mechanisms.add(mechanism)

        if item.get("anchor_kind") not in {"recurring-signature", "iconic-counterpoint"}:
            errors.append(f"{label}: invalid anchor_kind {item.get('anchor_kind')!r}")

        look = look_map.get(item.get("look_id"))
        if look is None:
            errors.append(f"{label}: unknown look_id {item.get('look_id')!r}")
        elif item.get("scene") != look.get("scene"):
            errors.append(f"{label}: scene does not match corpus look {item.get('look_id')}")

        if not is_https_url(item.get("source_page")):
            errors.append(f"{label}: source_page must be an HTTPS URL")
        elif item["source_page"] not in source_registry:
            errors.append(f"{label}: source_page is not registered in sources.md")
        if not is_https_url(item.get("image_url")):
            errors.append(f"{label}: image_url must be an HTTPS URL")
        for field in ("principles", "scenario_tags", "goal_tags", "fit_tags"):
            value = item.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
                errors.append(f"{label}: {field} must be a non-empty string array")
        if item.get("exposure_level") not in {"low", "medium", "high"}:
            errors.append(f"{label}: invalid exposure_level {item.get('exposure_level')!r}")
        for field in ("transferability", "representativeness"):
            value = item.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
                errors.append(f"{label}: {field} must be an integer from 1 to 5")
        why = item.get("why_representative")
        if not isinstance(why, str) or len(why.split()) < 10:
            errors.append(f"{label}: why_representative must explain the selection")
        alt = item.get("alt")
        if not isinstance(alt, str) or len(alt.split()) < 8:
            errors.append(f"{label}: alt must be descriptive")
        try:
            date.fromisoformat(item.get("checked_at", ""))
        except (TypeError, ValueError):
            errors.append(f"{label}: checked_at must use ISO YYYY-MM-DD")
        if item.get("use") != "remote-reference-only":
            errors.append(f"{label}: use must be remote-reference-only")

    scene_groups = {
        "airport/off-duty": sum(item.get("scene") in {"airport", "off-duty"} for item in visuals),
        "stage": sum(item.get("scene") == "stage" for item in visuals),
        "formal-event": sum(item.get("scene") == "formal-event" for item in visuals),
    }
    if len(visuals) < 12:
        errors.append(f"canonical pool needs at least 12 visuals; found {len(visuals)}")
    for group, count in scene_groups.items():
        if count < 3:
            errors.append(f"canonical pool needs at least 3 {group} visuals; found {count}")
    recurring = sum(item.get("anchor_kind") == "recurring-signature" for item in visuals)
    iconic = sum(item.get("anchor_kind") == "iconic-counterpoint" for item in visuals)
    if recurring < 7 or iconic < 3:
        errors.append(f"anchor mix is too narrow: recurring={recurring}, iconic={iconic}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    scenes = sorted({item["scene"] for item in visuals})
    print(f"Validated {len(visuals)} remote visual references")
    print("Scenes: " + ", ".join(scenes))
    print(f"Anchor mix: recurring-signature={recurring}, iconic-counterpoint={iconic}")
    print("All images are marked remote-reference-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
