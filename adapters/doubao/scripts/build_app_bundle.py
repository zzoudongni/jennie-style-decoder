#!/usr/bin/env python3
"""Compile the 52-look research corpus into the Doubao single-page app bundle."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / ".agents/skills/translate-jennie-style"
DOUBAO = ROOT / "adapters/doubao"
PACKAGE = DOUBAO / "app-skill"
TEMPLATE = DOUBAO / "app-template.html"
CORPUS = SKILL / "references/look-corpus.jsonl"
VISUALS = SKILL / "references/visual-index.jsonl"
SOURCES = SKILL / "references/sources.md"
OUTPUT_JSON = PACKAGE / "references/looks.json"
OUTPUT_HTML = PACKAGE / "assets/JENNIE_STYLE_DECODER_APP.html"
OUTPUT_ZIP = DOUBAO / "jennie-style-decoder-doubao-app.zip"


MECHANISM_PATTERNS = [
    ("feminine-utilitarian", ("lace", "lingerie", "bra", "sheer", "satin", "feather"), ("denim", "leather", "cargo", "technical", "boot", "utility", "bomber", "moto")),
    ("volume-contrast", ("oversized", "baggy", "wide", "roomy", "relaxed"), ("fitted", "compact", "cropped", "short", "micro", "slim")),
    ("texture-layering", ("texture contrast", "tweed", "knit", "flannel", "sequin", "fuzzy", "ruffle", "openwork", "translucent"), ()),
    ("structural-accessories", ("double belt", "waist chain", "structural jewelry", "narrow glasses", "cat-eye", "statement bag", "scarf"), ()),
    ("color-story", ("red", "burgundy", "pink", "blue", "white", "monochrome", "color repetition", "theme color"), ()),
]

GARMENT_PATTERNS = [
    (r"underwear|lingerie|\bbra\b", "内衣式上装"), (r"corset|bustier", "束身结构"),
    (r"camisole|slip top", "吊带上衣"), (r"halter", "挂脖上衣"), (r"tank", "背心"),
    (r"t-?shirt|\btee\b", "T恤"), (r"shirt", "衬衫"), (r"knit|sweater|cardigan", "针织"),
    (r"bomber", "飞行夹克"), (r"moto", "机车外套"), (r"jacket", "夹克"),
    (r"blazer|suit|tailor", "西装/剪裁"), (r"coat|cape", "长外层"),
    (r"cargo", "工装裤"), (r"jeans|denim trouser|denim pants", "牛仔裤"),
    (r"trouser|pants", "长裤"), (r"shorts", "短裤"), (r"micro skirt|mini skirt|\bmini\b", "短裙"),
    (r"maxi skirt|long skirt|skirt", "半裙"), (r"dress|gown", "连衣裙"),
    (r"tights|hosiery|fishnet", "丝袜/网袜"), (r"tall boot|knee-high|over-knee", "长靴"),
    (r"boot", "靴子"), (r"pump|heel|slingback", "高跟鞋"), (r"sneaker", "运动鞋"),
    (r"belt", "腰带"), (r"chain", "链条配饰"), (r"sunglasses|glasses", "窄框眼镜"),
    (r"scarf", "围巾"), (r"glove", "手套"), (r"hat|cap|beanie", "帽子"),
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_sources(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        source = re.search(r"`(S\d+)`", line)
        urls = re.findall(r"https?://\S+", line)
        if source and urls:
            result[source.group(1)] = urls[-1].rstrip(".,)")
    return result


def flatten(record: dict) -> str:
    values: list[str] = [str(record.get("title", "")), str(record.get("ordinary_translation", ""))]
    for field in ("observed_items", "silhouette", "palette", "textures", "proportion_devices", "accessories", "styling_devices"):
        values.extend(str(value) for value in record.get(field, []))
    return " ".join(values).lower()


def mechanism_family(record: dict, visual: dict | None) -> str:
    text = flatten(record) + " " + (visual or {}).get("core_mechanism", "").lower()
    for family, required, companion in MECHANISM_PATTERNS:
        if any(term in text for term in required) and (not companion or any(term in text for term in companion)):
            return family
    if any(term in text for term in ("stage", "dramatic", "theatrical", "performance", "movement", "couture", "micro")):
        return "scene-amplification"
    return "structural-accessories"


def garment_tags(record: dict) -> list[str]:
    text = flatten(record)
    tags: list[str] = []
    for pattern, label in GARMENT_PATTERNS:
        if re.search(pattern, text) and label not in tags:
            tags.append(label)
    return tags[:7] or ["基础单品", "结构重点"]


def exposure_level(record: dict, visual: dict | None) -> str:
    if visual and visual.get("exposure_level"):
        return visual["exposure_level"]
    text = flatten(record)
    high = ("underwear", "lingerie", "bra", "sheer", "transparent", "micro", "plunging", "bare midriff", "corset", "bustier")
    medium = ("cropped", "crop top", "mini", "shorts", "sleeveless", "off-shoulder", "low-rise", "slit")
    if any(term in text for term in high):
        return "high"
    if any(term in text for term in medium):
        return "medium"
    return "low"


def scenario_tags(record: dict, visual: dict | None) -> list[str]:
    tags = set((visual or {}).get("scenario_tags", []))
    scene = record["scene"]
    if scene in {"airport", "off-duty"}:
        tags.update(("casual", "commute", "date"))
    elif scene == "formal-event":
        tags.update(("formal", "date"))
    else:
        tags.update(("festival", "nightlife", "date"))
    text = flatten(record)
    if any(term in text for term in ("sheer", "bra", "lingerie", "micro", "slit", "shorts")):
        tags.add("island_holiday")
    return sorted(tags)


def material_tags(record: dict) -> list[str]:
    text = flatten(record)
    mapping = {
        "cotton": ("cotton", "jersey", "t-shirt"), "knit": ("knit", "sweater", "cardigan"),
        "denim": ("denim", "jeans"), "technical": ("technical", "nylon", "cargo", "sportswear"),
        "leather": ("leather", "moto"), "suede": ("suede",), "linen": ("linen",),
        "satin_silklike": ("satin", "silk"), "lace": ("lace",), "sheer_mesh": ("sheer", "mesh", "fishnet", "hosiery"),
        "feather_fringe_fuzzy": ("feather", "fringe", "fuzzy", "fur", "shearling"), "tweed": ("tweed",),
    }
    return [key for key, terms in mapping.items() if any(term in text for term in terms)]


def style_tags(record: dict) -> list[str]:
    family = mechanism_family(record, None)
    mapping = {
        "feminine-utilitarian": ["feminine_romantic", "bold_sexy", "experimental_mix"],
        "volume-contrast": ["casual_chill", "cool_street", "experimental_mix"],
        "color-story": ["minimal_basics", "feminine_romantic", "experimental_mix"],
        "texture-layering": ["feminine_romantic", "experimental_mix"],
        "structural-accessories": ["minimal_basics", "cool_street"],
        "scene-amplification": ["bold_sexy", "experimental_mix"],
    }
    return mapping[family]


def choose_source(record: dict, visual: dict | None, sources: dict[str, str]) -> str:
    if visual and visual.get("source_page"):
        return visual["source_page"]
    ids = record.get("source_ids", [])
    first_party = [sid for sid in ids if int(sid[1:]) >= 38 and sid in sources]
    for sid in first_party + ids:
        if sid in sources:
            return sources[sid]
    raise ValueError(f"No source URL for {record['id']}")


def build_records() -> list[dict]:
    corpus = read_jsonl(CORPUS)
    visuals = {row["look_id"]: row for row in read_jsonl(VISUALS)}
    sources = parse_sources(SOURCES)
    result: list[dict] = []
    for record in corpus:
        visual = visuals.get(record["id"])
        family = mechanism_family(record, visual)
        result.append({
            "lookId": record["id"], "date": record["date"], "scene": record["scene"],
            "title": record["title"], "sourceIds": record.get("source_ids", []),
            "sourceUrl": choose_source(record, visual, sources),
            "evidenceTier": record.get("evidence_tier", "B"), "confidence": record.get("confidence", "medium"),
            "imageUrl": (visual or {}).get("image_url"), "publisher": (visual or {}).get("publisher", "JENNIE / source page"),
            "alt": (visual or {}).get("alt", f"Source-linked visual record for {record['id']}"),
            "mechanismFamily": family, "coreMechanism": (visual or {}).get("core_mechanism", family),
            "scenarioTags": scenario_tags(record, visual), "goalTags": (visual or {}).get("goal_tags", []),
            "fitTags": (visual or {}).get("fit_tags", []), "styleTags": style_tags(record),
            "exposureLevel": exposure_level(record, visual), "materialTags": material_tags(record),
            "garmentTagsZh": garment_tags(record), "palette": record.get("palette", []), "textures": record.get("textures", []),
            "silhouette": record.get("silhouette", []), "stylingDevices": record.get("styling_devices", []),
            "ordinaryTranslation": record.get("ordinary_translation", ""),
            "representativeness": (visual or {}).get("representativeness", 4 if record.get("confidence") == "high" else 3),
            "transferability": (visual or {}).get("transferability", 4 if record["scene"] != "stage" else 3),
            "visualMode": "remote-image" if visual and visual.get("image_url") else "source-linked-structure-card",
        })
    return result


def write_bundle(records: list[dict]) -> None:
    PACKAGE.joinpath("assets").mkdir(parents=True, exist_ok=True)
    PACKAGE.joinpath("references").mkdir(parents=True, exist_ok=True)
    data = {"schemaVersion": 2, "lookCount": len(records), "stableImageCount": sum(bool(r["imageUrl"]) for r in records), "looks": records}
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    marker = "__JENNIE_LOOK_DATA__"
    if template.count(marker) != 1:
        raise ValueError(f"Template must contain {marker} exactly once")
    OUTPUT_HTML.write_text(template.replace(marker, json.dumps(data, ensure_ascii=False, separators=(",", ":"))), encoding="utf-8")


def make_zip() -> None:
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(PACKAGE))


def main() -> None:
    records = build_records()
    write_bundle(records)
    make_zip()
    print(f"Built {OUTPUT_HTML.relative_to(ROOT)} with {len(records)} looks")
    print(f"Stable remote images: {sum(bool(r['imageUrl']) for r in records)}")
    print(f"ZIP: {OUTPUT_ZIP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
