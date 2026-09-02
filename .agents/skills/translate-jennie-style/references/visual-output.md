# Visual-first output protocol

Fashion analysis should be seen and read together. Use images as evidence, not decoration.

## Image selection order

1. Choose the styling principle or personalized formula to explain.
2. Select a corpus look that visibly demonstrates that exact principle.
3. Search for the clearest full- or three-quarter-body image from an official source or the original fashion publisher.
4. Verify that the pictured look matches the corpus record and source page.
5. Embed the remote image with descriptive alt text and link the publisher immediately below it.

Use `references/visual-index.jsonl` as the canonical shortlist. Refresh remote URLs with live image search when needed because they can expire.

## Fixed versus dynamic behavior

Use a two-layer system:

- **Canonical pool:** 12 manually curated anchor looks. The pool is fixed until research is refreshed so the analysis remains coherent and representative.
- **Dynamic selection:** the images shown in a particular answer are selected from that pool according to report coverage or the user's scenario, goals, fit evidence, and exposure comfort. Do not always output the same images.

For a style report, use about **70% recurring-signature anchors** and **30% iconic/counterpoint anchors**. Do not rank a look highly merely because it is easy to copy.

## Required coverage

### One-page Jennie style summary (default)

Keep the initial report visibly compact enough to scan as one page:

- use one precise headline conclusion;
- show the six characteristics as six short visual cells or rows;
- use one representative image per characteristic, with up to two additional cross-scene anchors when essential;
- cap the whole summary at 6–8 images and about 450 Chinese characters excluding captions and source labels;
- give each characteristic one mechanism sentence and one transfer sentence;
- finish with one compact grammar line: `交界 → 视觉增量 → 风格冲突 → 定调细节`;
- offer “展开完整证据报告” instead of appending it automatically.

The one-page summary is a navigation layer, not the full proof set. Select images dynamically from the canonical pool and recent sourced additions. Rotate valid anchors between runs where several looks prove the same mechanism; do not always lead with the same look.

Run `scripts/select_visuals.py summary --variant N` as the default one-page selector. Change `N` between trials or derive it from the current task so equally valid anchors rotate without becoming random or unvetted.

### Full evidence report (only when requested)

Use `references/style-evidence-clusters.json`. For every characteristic:

- show 3–5 supporting looks;
- show one clearly labeled counterexample or boundary look;
- use a maximum of one sentence beneath each image;
- explain the repeated pattern only after the images;
- include “你应该看哪里” with exactly three cluster-level observations;
- state how the counterexample limits the conclusion.

Across the full report, use at least 18 unique looks. Do not reuse one look in more than three feature clusters. The current six clusters create 31 image placements from 18 unique looks.

Run `scripts/select_visuals.py report` to obtain the evidence plan. Items without a checked image URL require live image search against their corpus sources.

### Personalized translation

Show 2–3 closely matched Jennie references for each of the three outfit formulas. Select dynamically rather than using the same images for everyone. Within one formula, the references must demonstrate the same mechanism in different scenes, exposure levels, or intensities. The images illustrate the relationship being preserved—not an instruction to copy the entire outfit.

Run `scripts/select_visuals.py personal --profile profile.json` as a ranking aid for the lead image of each formula, then add one or two corroborating looks from the same evidence cluster. Keep three different `core_mechanism` values. Favor scenario and goal fit, then transferability; use representativeness to break ties.

## Feature evidence-cluster format

```markdown
## 特点：[feature title]

[3–5 supporting images, each with one-line date/scene caption and source]

### 这组图共同出现了什么
1. [cluster observation]
2. [cluster observation]
3. [cluster observation]

### 反例/边界
[one image + one sentence explaining why the rule is not absolute]

### 场景化迁移
[one concise rule]
```

Use the detailed card below when analyzing a single image inside a personalized formula.

## Single evidence-card format

```markdown
### 参考图：[short principle name]

![Descriptive alt text: Jennie wearing ...](direct-image-url)

图源：[Publisher — article title](source-page-url) · [look date/scene]

**看这三处**

1. [volume or proportion relationship]
2. [color or texture hierarchy]
3. [accessory/focal-point function]

**转译时保留：** [the styling relationship]
**可以按需要变化：** [brand, exposure, heel, fastening or exact garment; do not imply that boldness requires celebrity status]
```

For a personalized formula, add:

```markdown
**与你的连接：** [why this image matches the user's fit evidence, scenario and comfort]
```

## Visual annotation rules

- Limit “看这三处” to three observations so the image remains easy to read.
- Point to visible garment relationships: hem positions, volume, color blocks, texture, shoe weight, or accessory placement.
- Separate visible observation from styling inference. Say “外套明显比内层宽松” before saying “它建立了体积反差.”
- Do not comment on attractiveness, weight, body value, or speculate about measurements.
- Do not select close-up beauty portraits for a silhouette lesson.
- Avoid collages when individual looks cannot be distinguished.

## Copyright and attribution

- Keep celebrity/editorial images remote; never place them in `assets/` or commit image files to GitHub.
- Prefer official artist videos, Vogue, W, Teen Vogue, or another original editorial publisher already listed in `sources.md`.
- Preserve watermarks and original framing. Do not create derivative crops.
- Attribute publisher and link to the source page directly beneath every image.
- If remote embedding is blocked, show a source-page link with a specific description instead of a broken image or unauthorized copy.
- Do not imply that remote images are covered by this repository's MIT License.

## Accessibility and failure handling

- Alt text should identify garments, palette, silhouette, and scene; do not write “Jennie look 1.”
- Keep the written takeaway even when an image fails to load.
- Never invent a visual detail that is not visible or supported by the source.
- If no reliable image is available, state that limitation and use a different corpus look that demonstrates the same principle.
