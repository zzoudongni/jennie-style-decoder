#!/usr/bin/env python3
"""Build a private or public-preview Doubao bundle with embedded reference images."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from collections import defaultdict
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_app_bundle import DOUBAO, TEMPLATE, build_records  # noqa: E402


def encode_webp(path: Path, max_width: int, max_height: int, quality: int) -> tuple[str, str, int]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, "WEBP", quality=quality, method=6)
    blob = buffer.getvalue()
    digest = hashlib.sha256(blob).hexdigest()
    return f"data:image/webp;base64,{base64.b64encode(blob).decode('ascii')}", digest, len(blob)


def read_manifest(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("images", payload)
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest must contain a non-empty images list")
    return entries


def build_payload(image_dir: Path, manifest_path: Path, max_width: int, max_height: int, quality: int, distribution: str) -> tuple[dict, list[dict]]:
    records = build_records()
    by_id = {record["lookId"]: record for record in records}
    entries = read_manifest(manifest_path)
    seen_files: set[str] = set()
    seen_hashes: dict[str, str] = {}
    variants: dict[str, list[dict]] = defaultdict(list)
    applied_overrides: dict[str, dict] = {}
    audit: list[dict] = []

    for index, entry in enumerate(entries, 1):
        filename = entry["filename"]
        look_id = entry["lookId"]
        if filename in seen_files:
            raise ValueError(f"Duplicate filename in manifest: {filename}")
        if look_id not in by_id:
            raise ValueError(f"Unknown lookId {look_id} for {filename}")
        path = image_dir / filename
        if not path.is_file():
            matches = list(image_dir.rglob(filename))
            if len(matches) != 1:
                raise FileNotFoundError(f"Expected one match for {filename}, found {len(matches)}")
            path = matches[0]
        overrides = entry.get("recordOverrides")
        if overrides:
            previous = applied_overrides.get(look_id)
            if previous is not None and previous != overrides:
                raise ValueError(f"Conflicting recordOverrides for {look_id}")
            by_id[look_id].update(overrides)
            applied_overrides[look_id] = overrides
        data_url, digest, byte_count = encode_webp(path, max_width, max_height, quality)
        if digest in seen_hashes:
            raise ValueError(f"Duplicate optimized image: {filename} and {seen_hashes[digest]}")
        seen_files.add(filename)
        seen_hashes[digest] = filename
        asset_id = f"local-{index:02d}-{digest[:10]}"
        exact_source_url = entry.get("sourceUrl") if "sourceUrl" in entry else None
        if exact_source_url:
            source_url = exact_source_url
            source_label = "查看原始发布"
            source_status = "exact-post"
        elif not overrides and by_id[look_id].get("sourceUrl"):
            source_url = by_id[look_id]["sourceUrl"]
            source_label = "查看造型记录来源"
            source_status = "look-record"
        else:
            source_url = None
            source_label = "图片来源待补充"
            source_status = "pending"
        variant = {
            "assetId": asset_id,
            "imageUrl": data_url,
            "sourceUrl": source_url,
            "sourceLabel": source_label,
            "alt": entry.get("alt", f"Jennie styling reference supplied by the user, asset {index:02d}"),
        }
        variants[look_id].append(variant)
        audit.append({
            "assetId": asset_id, "filename": filename, "lookId": look_id,
            "sourceUrl": source_url, "sourceStatus": source_status,
            "optimizedBytes": byte_count, "sha256": digest,
        })

    folder_images = sorted(
        path.name for path in image_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    missing = sorted(set(folder_images) - seen_files)
    extra = sorted(seen_files - set(folder_images))
    if missing or extra:
        raise ValueError(f"Manifest/folder mismatch; missing={missing}, extra={extra}")

    for look_id, image_variants in variants.items():
        by_id[look_id]["imageVariants"] = image_variants
        by_id[look_id]["visualMode"] = "embedded-local-image"

    payload = {
        "schemaVersion": 3,
        "distributionMode": distribution,
        "lookCount": len(records),
        "embeddedImageCount": len(audit),
        "embeddedLookCount": len(variants),
        "imageBackedLookCount": sum(bool(r.get("imageUrl") or r.get("imageVariants")) for r in records),
        "embeddedOnly": True,
        "preferImageBacked": True,
        "looks": records,
    }
    return payload, audit


def media_notice(audit: list[dict]) -> str:
    counts = defaultdict(int)
    for item in audit:
        counts[item["sourceStatus"]] += 1
    lines = [
        "# Third-party media notice / 第三方媒体说明",
        "",
        "本包中的照片不适用项目 MIT License，权利归原摄影师、媒体、艺人团队、品牌或其他合法权利人。",
        "图片已压缩为低分辨率 WebP，仅与具体穿搭评论、审美研究和风格教育同页展示，不作为原图库提供。",
        "",
        f"- 精确原帖来源：{counts['exact-post']} 张",
        f"- 对应造型记录来源：{counts['look-record']} 张",
        f"- 来源待补充：{counts['pending']} 张",
        "",
        "“造型记录来源”仅证明对应的造型研究记录，不宣称该链接是当前文件的最初发布地。",
        "",
        "## Removal and attribution",
        "",
        "权利人如需补充署名、修改来源或移除图片，请通过项目 GitHub Issue 联系维护者。",
        "",
        "| Asset | Look | Source status | Link |",
        "|---|---|---|---|",
    ]
    for item in audit:
        url = item.get("sourceUrl")
        link = f"[source]({url})" if url else "pending"
        lines.append(f"| {item['assetId']} | {item['lookId']} | {item['sourceStatus']} | {link} |")
    return "\n".join(lines) + "\n"


def write_bundle(payload: dict, audit: list[dict], output_zip: Path, distribution: str, sync_package_dir: Path | None = None) -> Path:
    marker = "__JENNIE_LOOK_DATA__"
    html = TEMPLATE.read_text(encoding="utf-8")
    if html.count(marker) != 1:
        raise ValueError(f"Template must contain {marker} exactly once")
    html = html.replace(marker, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    if distribution == "public-preview":
        footer = f"非官方粉丝研究测试版。系统含 52 条造型记录、{payload['embeddedImageCount']} 张低分辨率分析参考图；照片不在开源许可证内，权利归各自权利人。来源或删除请求请联系仓库维护者。"
    else:
        footer = f"研究系统含 52 套造型记录；本私人测试包内嵌 {payload['embeddedImageCount']} 张用户提供的去重参考图。仅供个人研究与测试，请勿重新公开分发照片。"
    html = html.replace(
        "研究样本 52 套，其中 13 套使用可稳定嵌入的出版社远程图；其余以来源链接＋造型结构卡呈现。照片版权归原作者/发布者，本工具不下载或再分发照片。",
        footer,
    )

    skill_name = "jennie-style-decoder-doubao-public-preview" if distribution == "public-preview" else "jennie-style-decoder-doubao-local-visual"
    skill_text = f"""---
name: {skill_name}
description: 在豆包应用生成中直接交付内嵌 {payload['embeddedImageCount']} 张去重参考图的 Jennie Style Decoder 单页应用。
---

# 执行要求

1. 直接读取并交付 `assets/JENNIE_STYLE_DECODER_APP.html`，不要重新缩减或重写图片数组。
2. HTML 已把全部参考图转成内嵌 WebP；不得替换成网络 URL，不得只保留前 5 张。
3. 保留 52 套造型数据、单页不重复、跨轮轮换、问卷提交与个性化方案功能。
4. 第 3 步必须完整保留：Keep / Adjust / Avoid、三套视觉公式、每套公式的 Jennie 逻辑、为你调整、强度、站立/坐下/走路/抬手试穿检查，以及主色层级、配饰结构、妆发态度、季节与室内外切换、材质桥接、7 天审美练习。
5. 上述建议必须由问卷数据动态生成；不得用空白卡片、通用占位句或仅有标题的模块代替。
6. 最终只交付可预览、可下载的单页 HTML，不要求用户再次上传图片。
7. 照片不在项目开源许可证内；保留来源状态、非官方声明与权利人删除渠道。
"""
    spec_title = "公开低清分析测试版" if distribution == "public-preview" else "本地视觉版"
    spec_text = f"""# {spec_title}验收规范

- 52 个唯一造型记录。
- {payload['embeddedImageCount']} 张唯一内嵌 WebP 图片，归入 {payload['embeddedLookCount']} 个可选造型组。
- 审美地图每次 6 张；个性化方案每次 6 张。
- 同一页不得重复 `lookId` 或 `assetId`。
- 同一造型的多角度照片只能跨轮换用，不能在同一页并列冒充两套造型。
- 不依赖本地路径、GitHub Raw 或第三方图床。
- 图片加载失败时显示对应结构卡，不拿其他常用图补位。
- 每套公式均须输出 `Jennie 逻辑`、`为你调整`、用户所选`强度`以及站立、坐下、走路、抬手四项`试穿检查`。
- 公式之后必须输出 `主色层级`、`配饰结构`、`妆发态度`、`季节与室内外切换`、`材质桥接`和完整的 `7 天审美练习`。
- 所有建议均随问卷选择变化；不得把任何一个建议模块删除、折叠为空或改成占位文案。
"""
    edition = "公开低清分析测试版" if distribution == "public-preview" else "本地视觉版"
    readme_text = f"""# Jennie Style Decoder 豆包{edition}

将整个 ZIP 上传到豆包的“应用生成”，让它直接交付 `assets/JENNIE_STYLE_DECODER_APP.html`。成品 HTML 已包含完整第 3 步建议系统，豆包不得重写或精简。

推荐提示词：`请完整读取压缩包并直接交付 assets/JENNIE_STYLE_DECODER_APP.html，不要从零重写。保留全部 53 张图、动态去重选图，以及第 3 步所有个性化建议模块；严格按 SKILL.md 和 APP_BUILD_SPEC.md 验收。`

本项目是非官方粉丝研究工具，与 Jennie Kim 及相关艺人团队、品牌和媒体无授权、合作或背书关系。照片不适用项目开源许可证，详见 `THIRD_PARTY_MEDIA.md`。

公开测试观察期：2026-09-07 至 2026-09-24（共 14 个工作日）。这一期限不构成版权授权或责任豁免。
"""

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        package = Path(temp_dir) / "jennie-style-decoder-doubao-local-visual"
        (package / "assets").mkdir(parents=True)
        (package / "references").mkdir(parents=True)
        (package / "assets/JENNIE_STYLE_DECODER_APP.html").write_text(html, encoding="utf-8")
        (package / "SKILL.md").write_text(skill_text, encoding="utf-8")
        (package / "APP_BUILD_SPEC.md").write_text(spec_text, encoding="utf-8")
        (package / "README.md").write_text(readme_text, encoding="utf-8")
        (package / "THIRD_PARTY_MEDIA.md").write_text(media_notice(audit), encoding="utf-8")
        (package / "references/local-visual-manifest.json").write_text(
            json.dumps({"count": len(audit), "images": audit}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if output_zip.exists():
            output_zip.unlink()
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(package.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(package))
        html_output = output_zip.with_suffix(".html")
        shutil.copy2(package / "assets/JENNIE_STYLE_DECODER_APP.html", html_output)
        if sync_package_dir:
            if sync_package_dir.exists():
                shutil.rmtree(sync_package_dir)
            shutil.copytree(package, sync_package_dir)
    return html_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    parser.add_argument("--max-width", type=int, default=900)
    parser.add_argument("--max-height", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=72)
    parser.add_argument("--distribution", choices=("private", "public-preview"), default="private")
    parser.add_argument("--sync-package-dir", type=Path)
    args = parser.parse_args()
    payload, audit = build_payload(args.image_dir, args.manifest, args.max_width, args.max_height, args.quality, args.distribution)
    html_output = write_bundle(payload, audit, args.output_zip, args.distribution, args.sync_package_dir)
    print(f"Built: {args.output_zip}")
    print(f"HTML: {html_output}")
    print(f"52 looks; {len(audit)} embedded images; {payload['embeddedLookCount']} embedded look groups")


if __name__ == "__main__":
    main()
