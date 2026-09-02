#!/usr/bin/env python3
"""Validate feature-level image evidence clusters against the look corpus."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


REQUIRED = {
    "feature_id",
    "title_cn",
    "thesis_cn",
    "support_look_ids",
    "counterexample_look_id",
    "look_for_cn",
    "transfer_cn",
}


def read_jsonl_ids(path: Path) -> set[str]:
    ids = set()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name} line {line_no}: {exc}") from exc
        if item.get("id"):
            ids.add(item["id"])
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clusters", type=Path)
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()

    errors = []
    try:
        data = json.loads(args.clusters.read_text(encoding="utf-8"))
        corpus_ids = read_jsonl_ids(args.corpus)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        print("ERROR: clusters root must contain a features array", file=sys.stderr)
        return 1
    if not 5 <= len(features) <= 7:
        errors.append(f"report needs 5–7 core features; found {len(features)}")

    feature_ids = set()
    all_placements = []
    for index, feature in enumerate(features, 1):
        label = f"feature {index}"
        missing = sorted(REQUIRED - feature.keys())
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
        feature_id = feature.get("feature_id")
        if not isinstance(feature_id, str) or not feature_id:
            errors.append(f"{label}: feature_id must be non-empty")
        elif feature_id in feature_ids:
            errors.append(f"{label}: duplicate feature_id {feature_id}")
        else:
            feature_ids.add(feature_id)

        support = feature.get("support_look_ids")
        if not isinstance(support, list) or not 3 <= len(support) <= 5:
            errors.append(f"{label}: support_look_ids must contain 3–5 looks")
            support = []
        elif len(support) != len(set(support)):
            errors.append(f"{label}: duplicate supporting look")
        counterexample = feature.get("counterexample_look_id")
        if counterexample in support:
            errors.append(f"{label}: counterexample duplicates a supporting look")
        cluster_looks = support + ([counterexample] if isinstance(counterexample, str) else [])
        unknown = sorted(set(cluster_looks) - corpus_ids)
        if unknown:
            errors.append(f"{label}: unknown corpus looks: {', '.join(unknown)}")
        if not 4 <= len(cluster_looks) <= 6:
            errors.append(f"{label}: total image evidence must contain 4–6 looks")
        all_placements.extend(cluster_looks)

        look_for = feature.get("look_for_cn")
        if not isinstance(look_for, list) or len(look_for) != 3 or not all(isinstance(x, str) and x for x in look_for):
            errors.append(f"{label}: look_for_cn must contain exactly three observations")
        for field in ("title_cn", "thesis_cn", "transfer_cn"):
            if not isinstance(feature.get(field), str) or not feature.get(field):
                errors.append(f"{label}: {field} must be non-empty")

    reuse = Counter(all_placements)
    overused = sorted(look_id for look_id, count in reuse.items() if count > 3)
    if overused:
        errors.append("looks reused in more than three features: " + ", ".join(overused))
    unique_count = len(reuse)
    if unique_count < 18:
        errors.append(f"report needs at least 18 unique looks across clusters; found {unique_count}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(features)} feature evidence clusters")
    print(f"Image placements: {len(all_placements)}; unique looks: {unique_count}")
    print(f"Maximum cross-feature reuse: {max(reuse.values(), default=0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
