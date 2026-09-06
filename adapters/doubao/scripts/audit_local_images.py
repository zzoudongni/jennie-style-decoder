#!/usr/bin/env python3
"""Inventory, perceptually de-duplicate, and contact-sheet local visual assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def dhash(image: Image.Image, size: int = 16) -> int:
    gray = ImageOps.grayscale(image).resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(gray.get_flattened_data())
    value = 0
    for y in range(size):
        row = y * (size + 1)
        for x in range(size):
            value = (value << 1) | int(pixels[row + x] > pixels[row + x + 1])
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(paths: list[Path]) -> list[dict]:
    records: list[dict] = []
    for root in paths:
        for path in sorted(root.iterdir()):
            if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
                continue
            try:
                with Image.open(path) as image:
                    width, height = image.size
                    records.append({
                        "path": str(path), "name": path.name, "root": str(root),
                        "width": width, "height": height, "bytes": path.stat().st_size,
                        "sha256": sha256(path), "dhash": f"{dhash(image):064x}",
                    })
            except Exception as error:
                records.append({"path": str(path), "name": path.name, "root": str(root), "error": str(error)})
    return records


def group_duplicates(records: list[dict], threshold: int) -> list[list[int]]:
    valid = [index for index, row in enumerate(records) if "error" not in row]
    parent = list(range(len(records)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for offset, i in enumerate(valid):
        for j in valid[offset + 1:]:
            if records[i]["sha256"] == records[j]["sha256"]:
                union(i, j)
                continue
            distance = hamming(int(records[i]["dhash"], 16), int(records[j]["dhash"], 16))
            aspect_i = records[i]["width"] / records[i]["height"]
            aspect_j = records[j]["width"] / records[j]["height"]
            if distance <= threshold and abs(aspect_i - aspect_j) <= 0.04:
                union(i, j)
    groups: dict[int, list[int]] = {}
    for i in valid:
        groups.setdefault(find(i), []).append(i)
    return [members for members in groups.values() if len(members) > 1]


def contact_sheet(records: list[dict], output: Path) -> None:
    valid = [row for row in records if "error" not in row]
    cell_w, cell_h, thumb_h, columns = 260, 360, 292, 5
    rows = (len(valid) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "#f2eee7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=15)
    small = ImageFont.load_default(size=12)
    for index, row in enumerate(valid):
        x, y = (index % columns) * cell_w, (index // columns) * cell_h
        with Image.open(row["path"]) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            thumb = ImageOps.contain(image, (cell_w - 16, thumb_h - 12), Image.Resampling.LANCZOS)
            tx, ty = x + (cell_w - thumb.width) // 2, y + 6 + (thumb_h - thumb.height) // 2
            sheet.paste(thumb, (tx, ty))
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#c8beb0")
        draw.text((x + 9, y + thumb_h + 6), f"{index + 1:02d}", fill="#9d2925", font=font)
        name = row["name"]
        draw.text((x + 42, y + thumb_h + 6), name[:30], fill="#111", font=small)
        draw.text((x + 9, y + thumb_h + 29), f"{row['width']}x{row['height']}  {row['bytes']//1024} KB", fill="#665f56", font=small)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=90)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--threshold", type=int, default=8)
    args = parser.parse_args()
    records = collect(args.paths)
    duplicates = group_duplicates(records, args.threshold)
    payload = {"count": len(records), "records": records, "duplicateGroups": duplicates}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contact_sheet(records, args.sheet)
    print(f"Images: {len(records)}")
    print(f"Duplicate groups: {len(duplicates)}")
    for group in duplicates:
        print("  " + " | ".join(records[index]["name"] for index in group))
    print(f"Report: {args.output}")
    print(f"Contact sheet: {args.sheet}")


if __name__ == "__main__":
    main()
