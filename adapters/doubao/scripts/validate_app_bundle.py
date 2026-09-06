#!/usr/bin/env python3
"""Validate the generated Doubao app bundle and its selection invariants."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import zipfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOUBAO = ROOT / "adapters/doubao"
PACKAGE = DOUBAO / "app-skill"
HTML_PATH = PACKAGE / "assets/JENNIE_STYLE_DECODER_APP.html"
ZIP_PATH = DOUBAO / "jennie-style-decoder-doubao-app.zip"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    data_match = re.search(r"const DATA=(\{.*?\});\nconst LOOKS=", html, re.S)
    if not data_match:
        fail("cannot find embedded DATA payload")
    payload = json.loads(data_match.group(1))
    looks = payload.get("looks", [])
    ids = [look["lookId"] for look in looks]
    families = Counter(look["mechanismFamily"] for look in looks)
    if len(looks) != 52 or len(set(ids)) != 52:
        fail("embedded payload must contain exactly 52 unique look IDs")
    if len(families) != 6 or not all(families.values()):
        fail(f"all six mechanism families must be populated: {families}")
    variants = [variant for look in looks for variant in look.get("imageVariants", [])]
    if payload.get("embeddedOnly"):
        asset_ids = [variant.get("assetId") for variant in variants]
        image_urls = [variant.get("imageUrl") for variant in variants]
        if len(variants) != payload.get("embeddedImageCount") or len(set(asset_ids)) != len(variants):
            fail("embedded image count or asset IDs are inconsistent")
        if len(set(image_urls)) != len(variants) or any(not url.startswith("data:image/webp;base64,") for url in image_urls):
            fail("embedded images must be unique WebP data URLs")
        embedded_look_count = sum(bool(look.get("imageVariants")) for look in looks)
        if embedded_look_count != payload.get("embeddedLookCount"):
            fail("embedded look-group count is inconsistent")
    else:
        urls = [look["imageUrl"] for look in looks if look.get("imageUrl")]
        if len(urls) != 13 or len(set(urls)) != 13:
            fail("remote edition must contain exactly 13 unique stable image URLs")
        if any(not look.get("sourceUrl") for look in looks):
            fail("every remote-edition look requires a source URL")
    if "__JENNIE_LOOK_DATA__" in html:
        fail("unresolved data marker in generated HTML")
    if any(token in html for token in ("file://", "/Users/", "/var/folders/")):
        fail("generated HTML contains a local file path")
    match = re.search(r'<script id="jsd-app-logic">\n([\s\S]*?)\n</script>', html)
    if not match:
        fail("cannot find inline app logic")
    logic = match.group(1)
    tests = r'''
const profiles=[
  {scenario:['casual','date'],goals:['defined_waist'],intensity:'flexible',element_preferences:{low_rise:'often_wear'},current_materials:['denim'],open_to_materials:['lace'],target_style:['experimental_mix']},
  {scenario:['nightlife'],goals:['learn_logic'],intensity:'full',element_preferences:{underwear_as_outerwear:'willing_to_try',micro_bottom:'willing_to_try'},current_materials:['leather'],open_to_materials:['sheer_mesh'],target_style:['bold_sexy']},
  {scenario:['commute'],goals:['cleaner_lines'],intensity:'daily',element_preferences:{},current_materials:['cotton','knit'],open_to_materials:[],target_style:['minimal_basics']}
];
for(let run=0;run<12;run++)for(const p of profiles){
  const pairs=JennieDecoderCore.selectPlan(p,[],run), flat=pairs.flat();
  if(flat.length!==6)throw new Error('result does not contain 6 references');
  if(new Set(flat.map(x=>x.lookId)).size!==6)throw new Error('duplicate lookId');
  const u=flat.map(x=>x.imageUrl).filter(Boolean);if(new Set(u).size!==u.length)throw new Error('duplicate imageUrl');
  if(new Set(pairs.map(x=>x[0].mechanismFamily)).size!==3)throw new Error('lead mechanisms not distinct');
  const advice=JennieDecoderCore.buildAdvice(p,pairs);
  if(advice.formulas.length!==3)throw new Error('missing formula advice');
  if(advice.formulas.some(x=>!x.logic||!x.adjust||!x.strength||x.checks.length!==4))throw new Error('formula advice is incomplete');
  if(!advice.color.base||!advice.accessories.main||!advice.beauty||!advice.climate||!advice.materials.bridge)throw new Error('global styling advice is incomplete');
  if(advice.practice.length!==7||advice.practice.some(x=>!x))throw new Error('seven-day practice is incomplete');
}
const batches=[];for(let run=0;run<6;run++)batches.push(JennieDecoderCore.selectUnique({scenario:['casual']},6,[],run,true).map(x=>x.lookId).join(','));
if(new Set(batches).size<4)throw new Error('rotation is insufficient');
const allAssets=new Set(JennieDecoderCore.LOOKS.flatMap(x=>(x.imageVariants||[]).map(v=>v.assetId)));
const reachable=new Set();for(let run=0;run<700;run++)JennieDecoderCore.selectableLooks(run).forEach(x=>{if(x.assetId)reachable.add(x.assetId)});
if(reachable.size!==allAssets.size)throw new Error(`only ${reachable.size}/${allAssets.size} embedded assets are reachable`);
console.log('JS selection tests passed');
'''
    with tempfile.TemporaryDirectory() as temp:
        script = Path(temp) / "app-test.js"
        script.write_text(logic + tests, encoding="utf-8")
        subprocess.run(["node", "--check", str(script)], check=True)
        subprocess.run(["node", str(script)], check=True)

    if not ZIP_PATH.exists():
        fail("ZIP bundle is missing")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = set(archive.namelist())
    required = {"SKILL.md", "APP_BUILD_SPEC.md", "README.md", "assets/JENNIE_STYLE_DECODER_APP.html"}
    if payload.get("embeddedOnly"):
        required.update({"THIRD_PARTY_MEDIA.md", "references/local-visual-manifest.json"})
    else:
        required.add("references/looks.json")
    if not required.issubset(names):
        fail(f"ZIP bundle missing: {sorted(required - names)}")
    required_modules = (
        "JENNIE 逻辑", "为你调整", "试穿检查", "主色层级", "配饰结构",
        "妆发态度", "季节与室内外切换", "材质桥接", "7 天审美练习",
    )
    missing_modules = [module for module in required_modules if module not in html]
    if missing_modules:
        fail(f"personalized result modules missing from HTML: {missing_modules}")
    print(f"PASS: 52 looks, {len(variants) if variants else 13} images, six families {dict(families)}")
    if variants:
        print(f"PASS: all {len(variants)} embedded assets are reachable across rotations")
    print("PASS: no duplicate look or image in 36 simulated personalized results")
    print("PASS: all mandatory personalized advice modules produce non-empty content")
    print("PASS: ZIP contains all required Doubao app-builder files")


if __name__ == "__main__":
    main()
