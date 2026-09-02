#!/usr/bin/env python3
"""Select representative or profile-matched visuals from the canonical pool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPOSURE_RANK = {"low": 0, "medium": 1, "high": 2}
SCENARIO_ALIASES = {
    "city_travel": {"casual", "date"},
    "island_holiday": {"casual", "date", "festival"},
    "nightlife": {"date", "festival"},
}
ELEMENT_TERMS = {
    "low_neckline": {"plunging", "lingerie", "intimate", "minimal top"},
    "low_rise": {"low", "waist", "denim", "relaxed trouser"},
    "strapless": {"bustier", "strapless", "minimal top"},
    "camisole": {"camisole", "fitted top", "minimal top", "intimate"},
    "midriff": {"crop", "cropped", "compact base", "minimal inner"},
    "underwear_as_outerwear": {"lingerie", "underwear", "bra", "intimate"},
    "lace": {"lace", "feminine"},
    "sheer": {"sheer", "transparent"},
    "micro_bottom": {"micro", "mini", "short"},
    "high_slit": {"slit", "asymmetric"},
    "backless": {"backless", "open shoulder"},
    "tall_boots": {"boot", "western"},
    "stacked_hardware": {"belt", "chain", "hardware", "metal"},
}
MATERIAL_TERMS = {
    "cotton": {"cotton", "tee"},
    "knit": {"knit", "sweater"},
    "denim": {"denim", "jean"},
    "technical": {"technical", "cargo", "nylon"},
    "linen": {"linen"},
    "satin_silklike": {"satin", "silk", "smooth"},
    "lace": {"lace"},
    "sheer_mesh": {"sheer", "mesh", "transparent"},
    "leather": {"leather", "moto"},
    "suede": {"suede", "western"},
    "feather_fringe_fuzzy": {"feather", "fringe", "furry", "texture"},
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name} line {line_no}: {exc}") from exc
    return records


def load_clusters(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        raise ValueError("cluster file must contain a features array")
    return features


def resolve_look(look_id: str, role: str, visual_map: dict[str, dict], corpus_map: dict[str, dict]) -> dict:
    if look_id in visual_map:
        return {**visual_map[look_id], "evidence_role": role, "needs_live_image_search": False}
    look = corpus_map.get(look_id)
    if look is None:
        raise ValueError(f"unknown look_id {look_id}")
    return {
        "look_id": look_id,
        "scene": look["scene"],
        "title": look["title"],
        "source_ids": look["source_ids"],
        "evidence_role": role,
        "needs_live_image_search": True,
    }


def select_report(records: list[dict], corpus: list[dict], clusters: list[dict]) -> list[dict]:
    visual_map = {item["look_id"]: item for item in records}
    corpus_map = {item["id"]: item for item in corpus}
    plan = []
    for feature in clusters:
        images = [
            resolve_look(look_id, "support", visual_map, corpus_map)
            for look_id in feature["support_look_ids"]
        ]
        images.append(resolve_look(feature["counterexample_look_id"], "counterexample", visual_map, corpus_map))
        plan.append({**feature, "images": images})
    return plan


def select_summary(records: list[dict], clusters: list[dict], variant: int) -> list[dict]:
    """Choose one sourced anchor per feature while avoiding repeated looks."""
    visual_map = {item["look_id"]: item for item in records}
    used: set[str] = set()
    summary = []
    for feature_index, feature in enumerate(clusters):
        candidate_ids = [
            look_id
            for look_id in feature["support_look_ids"] + [feature["counterexample_look_id"]]
            if look_id in visual_map
        ]
        if not candidate_ids:
            raise ValueError(f"no canonical visual available for feature {feature['feature_id']}")
        offset = (variant + feature_index) % len(candidate_ids)
        rotated = candidate_ids[offset:] + candidate_ids[:offset]
        chosen_id = next((look_id for look_id in rotated if look_id not in used), rotated[0])
        used.add(chosen_id)
        summary.append({
            "feature_id": feature["feature_id"],
            "title_cn": feature["title_cn"],
            "thesis_cn": feature["thesis_cn"],
            "transfer_cn": feature["transfer_cn"],
            "image": visual_map[chosen_id],
        })
    return summary


def exposure_penalty(candidate: str, user: str) -> int:
    difference = EXPOSURE_RANK[candidate] - EXPOSURE_RANK[user]
    if difference <= 0:
        return 0
    return {1: 3, 2: 8}[difference]


def score_personal(
    item: dict,
    scenarios: set[str],
    goals: set[str],
    fits: set[str],
    exposure: str,
    intensity: str,
    preferred_elements: set[str],
    materials: set[str],
    target_style: set[str],
) -> tuple[int, list[str]]:
    score = item["representativeness"] * 2 + item["transferability"] * 2
    reasons = []
    scenario_matches = sorted(scenarios & set(item["scenario_tags"]))
    goal_matches = sorted(goals & set(item["goal_tags"]))
    fit_matches = sorted(fits & set(item["fit_tags"]))
    if scenario_matches:
        score += 10
        reasons.append("scenario=" + ",".join(scenario_matches))
    if goal_matches:
        score += 2 * len(goal_matches)
        reasons.append("goals=" + ",".join(goal_matches))
    if fit_matches:
        score += len(fit_matches)
        reasons.append("fit=" + ",".join(fit_matches))
    if item["anchor_kind"] == "recurring-signature":
        score += 2
        reasons.append("recurring-signature")
    penalty = exposure_penalty(item["exposure_level"], exposure)
    if penalty:
        score -= penalty
        reasons.append(f"exposure-translation=-{penalty}")
    elif item["exposure_level"] == exposure:
        score += 3
        reasons.append("exposure-direct-match")
    if intensity == "bold" and item["exposure_level"] == "high":
        score += 4
        reasons.append("same-intensity-bold")
    elif intensity == "quiet" and item["exposure_level"] == "low":
        score += 3
        reasons.append("same-intensity-quiet")

    searchable = " ".join([
        item.get("core_mechanism", ""),
        " ".join(item.get("principles", [])),
        item.get("why_representative", ""),
        item.get("alt", ""),
    ]).lower()
    element_hits = sorted(
        element for element in preferred_elements
        if any(term in searchable for term in ELEMENT_TERMS.get(element, set()))
    )
    if element_hits:
        score += min(6, 2 * len(element_hits))
        reasons.append("elements=" + ",".join(element_hits))
    material_hits = sorted(
        material for material in materials
        if any(term in searchable for term in MATERIAL_TERMS.get(material, set()))
    )
    if material_hits:
        score += min(3, len(material_hits))
        reasons.append("materials=" + ",".join(material_hits))
    if "experimental_mix" in target_style and item["anchor_kind"] == "iconic-counterpoint":
        score += 2
        reasons.append("target=experimental_mix")
    if "casual_chill" in target_style and item["transferability"] >= 4:
        score += 2
        reasons.append("target=casual_chill")
    if "bold_sexy" in target_style and item["exposure_level"] == "high":
        score += 2
        reasons.append("target=bold_sexy")
    return score, reasons


def select_personal(records: list[dict], profile: dict, extra_scenarios: list[str], clusters: list[dict]) -> list[dict]:
    raw_scenario = profile.get("scenario", "casual")
    scenarios = set(raw_scenario if isinstance(raw_scenario, list) else [raw_scenario])
    scenarios.update(extra_scenarios)
    for scenario in list(scenarios):
        scenarios.update(SCENARIO_ALIASES.get(scenario, set()))
    goals = set(profile.get("goals", []))
    fits = set(profile.get("top_fit", [])) | set(profile.get("pants_fit", []))
    exposure = profile.get("exposure", "medium")
    if exposure not in EXPOSURE_RANK:
        raise ValueError(f"unsupported exposure {exposure!r}")

    intensity = profile.get("intensity", "flexible")
    raw_preferences = profile.get("element_preferences", {}) or {}
    preferred_elements = set(profile.get("preferred_elements", [])) | {
        key for key, value in raw_preferences.items() if value in {"often_wear", "willing_to_try"}
    }
    materials = set(profile.get("current_materials", [])) | set(profile.get("open_to_materials", []))
    target_style = set(profile.get("target_style", []))

    ranked = []
    for item in records:
        score, reasons = score_personal(
            item, scenarios, goals, fits, exposure, intensity,
            preferred_elements, materials, target_style,
        )
        ranked.append((score, item, reasons))
    ranked.sort(key=lambda row: (-row[0], -row[1]["representativeness"], row[1]["visual_id"]))

    selected = []
    mechanisms = set()
    for score, item, reasons in ranked:
        if item["core_mechanism"] in mechanisms:
            continue
        selected.append({**item, "match_score": score, "match_reasons": reasons})
        mechanisms.add(item["core_mechanism"])
        if len(selected) == 3:
            break
    cluster_usage = set()
    image_usage = {item["look_id"] for item in selected}
    groups = []
    for lead in selected:
        candidates = [
            feature
            for feature in clusters
            if lead["look_id"] in feature["support_look_ids"] + [feature["counterexample_look_id"]]
            and feature["feature_id"] not in cluster_usage
        ]
        if not candidates:
            candidates = [
                feature
                for feature in clusters
                if lead["look_id"] in feature["support_look_ids"] + [feature["counterexample_look_id"]]
            ]
        feature = candidates[0] if candidates else None
        corroborating = []
        if feature:
            cluster_usage.add(feature["feature_id"])
            for look_id in feature["support_look_ids"] + [feature["counterexample_look_id"]]:
                if look_id == lead["look_id"] or look_id in image_usage:
                    continue
                corroborating.append(look_id)
                image_usage.add(look_id)
                if len(corroborating) == 2:
                    break
        groups.append(
            {
                "lead": lead,
                "evidence_feature_id": feature["feature_id"] if feature else None,
                "evidence_feature_title_cn": feature["title_cn"] if feature else None,
                "corroborating_look_ids": corroborating,
            }
        )
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("summary", "report", "personal"))
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--scenario", action="append", default=[], help="Add another scenario such as date")
    parser.add_argument("--ids-only", action="store_true", help="Print only selected visual IDs")
    parser.add_argument("--variant", type=int, default=0, help="Rotate equally valid one-page anchors")
    parser.add_argument(
        "--index",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references" / "visual-index.jsonl",
    )
    parser.add_argument(
        "--clusters",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references" / "style-evidence-clusters.json",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references" / "look-corpus.jsonl",
    )
    args = parser.parse_args()

    try:
        records = load_jsonl(args.index)
        clusters = load_clusters(args.clusters)
        if args.mode == "summary":
            selected = select_summary(records, clusters, args.variant)
        elif args.mode == "report":
            corpus = load_jsonl(args.corpus)
            selected = select_report(records, corpus, clusters)
        else:
            if args.profile is None:
                raise ValueError("--profile is required in personal mode")
            profile = json.loads(args.profile.read_text(encoding="utf-8"))
            selected = select_personal(records, profile, args.scenario, clusters)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.ids_only and args.mode == "summary":
        output = {
            item["feature_id"]: item["image"]["visual_id"]
            for item in selected
        }
    elif args.ids_only and args.mode == "report":
        output = {
            item["feature_id"]: [image["look_id"] for image in item["images"]]
            for item in selected
        }
    elif args.ids_only:
        output = [
            [item["lead"]["visual_id"], *item["corroborating_look_ids"]]
            for item in selected
        ]
    else:
        output = selected
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
