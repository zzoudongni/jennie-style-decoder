---
name: translate-jennie-style
description: Analyze Jennie Kim's recent fashion as an evidence-based, visual and explainable style system, show sourced reference images, and translate its styling logic into personalized, wearable outfit guidance. Use when a user asks for a Jennie style report, visual analysis of her airport/off-duty/stage/formal looks, help learning her styling logic, or a Jennie-inspired plan based on concrete fit experiences, measurements, goals, scenario, and exposure comfort. Do not use for virtual try-on, body-shape diagnosis, exact celebrity-item shopping, or medical/body-value judgments.
---

# Translate Jennie Style

Turn Jennie's styling into principles a user can understand and reuse. Preserve the logic—not her body, budget, or brands. Preserve exact devices such as low rise, underwear-as-outerwear, sheer layers, or micro proportions when the user actively wants them and the chosen scene supports them; being a non-celebrity is never a reason to dilute a look.

## Choose the route

- **Style report only:** read `references/style-findings.md`, `references/style-evidence-clusters.json`, and `references/visual-output.md`, then use the report format in `references/output-templates.md`.
- **Personal styling:** run the three-step flow below. Read `references/body-questionnaire.md`, `references/adaptation-rules.md`, `references/visual-output.md`, and `references/output-templates.md`.
- **New or refreshed research:** read `references/research-method.md`; update `references/sources.md` and `references/look-corpus.jsonl` before revising conclusions.
- **Analysis of a user-provided Jennie image:** describe only visible features first, separate observation from interpretation, then compare with the framework. Do not identify an item or brand unless the evidence supports it.

## Three-step user flow

### 1. Explain the style system

Default to a **one-page visual summary** before asking about the user. Organize the six characteristics from `references/style-evidence-clusters.json` into one compact page with:

- one precise conclusion;
- one anchor image and one short rule per characteristic;
- no more than 6–8 images total;
- a compact “style grammar” line and evidence-window note.

Do not print the full six-chapter evidence report by default. If the user asks to expand, audit, or see more proof, switch to **evidence mode** and show 3–5 supporting Jennie looks plus one labeled counterexample for each characteristic. Cover:

1. overall style tension;
2. silhouette and proportion;
3. color and texture;
4. accessories and beauty attitude;
5. how the logic changes across off-duty/airport, stage, and formal settings;
6. which elements transfer well to everyday life.

State the research window and evidence limits. Use “in the reviewed looks” rather than claiming a permanent truth about Jennie.

Every image must prove one named principle. Follow `references/visual-output.md`; do not add decorative celebrity images with no analysis. Resolve missing remote images from the corpus sources with live image search.

### 2. Collect concrete user information

Collect the nine quick questions in `references/body-questionnaire.md`, grouped into garment feedback, scene/expression, and current wardrobe language. Inside the scene group, record temperature and indoor/outdoor environment as two separate compact rows; do not add another step. Prefer a directly clickable checklist or form over asking the user to copy option letters and numbers. In Codex or another client that supports inline interactive HTML, copy `assets/profile-form.html` into the task-owned visualization directory and show it in conversation; its submit action sends the selected answers back to the chat. If interactive controls are unavailable, use the compact checkbox fallback in the questionnaire reference. Do not ask for Chinese clothing sizes, weight, a body-type label, or abstract shoulder/waist/hip and torso/leg classifications.

Do not compress exposure into one vague low/medium/high answer. Record individual preferences for low neckline, low rise, strapless, camisole, midriff, backless, underwear-as-outerwear, lace/sheer, micro hems or slits, boots, and stacked hardware as **often wear / willing to try / not this time**. Allow unanswered rows to mean “no strong preference.” Also distinguish materials already common in the wardrobe from materials the user is willing to explore.

Allow “不确定” for every visual or fit judgment. Measurements are optional. If the user supplies a photo, treat it as supplementary evidence and never infer exact measurements from it.

If the user has already provided enough information, do not repeat questions. Ask only for missing information that would materially change the result.

### 3. Produce the translation plan

Follow `references/adaptation-rules.md` and output:

- a one-sentence style direction;
- objective fit observations, with confidence labels where uncertain;
- **keep / adjust / avoid** recommendations;
- three outfit formulas for the user's main scenario, each paired with 2–3 closely matched Jennie reference looks showing the same mechanism at different intensities or scenes;
- a same-intensity version by default, plus a lower- or higher-exposure alternative only when the user's stated preference or another target scene makes it useful;
- a climate plan that separates the destination look from transit outerwear when cold weather or long outdoor exposure matters;
- accessories, hair/makeup attitude, and color guidance;
- a material bridge that starts from the user's familiar fabrics and shows which Jennie textures can be added directly or experimentally;
- a seven-day practice challenge using generic garment categories, not purchases.

Explain why each adjustment preserves a Jennie styling principle. Do not promise that clothing will make the user “look like Jennie.”

Place each reference image beside the formula it supports rather than collecting all images at the end. If an image cannot be embedded reliably, provide a clearly labeled source-page link and continue; never invent or substitute an unrelated look.

## Evidence and safety rules

- Separate **observed garment facts**, **editorial identification**, and **styling inference**.
- Prefer first-party video/interviews and clear dated imagery; use fashion publications for garment identification. See `references/research-method.md`.
- Do not invent exact brands, dates, measurements, or motives.
- Use the 13-look stable canonical pool in `references/visual-index.jsonl` for dependable embeds, then select dynamically from the full 52-look sourced corpus using `scripts/select_visuals.py`. A corpus result marked `needs_live_image_search` must be resolved against its registered source at answer time; use live image search to refresh broken URLs or the requested date window, not to choose random unvetted looks.
- Do not download, repackage, crop, remove watermarks from, or commit Jennie/editorial photographs to the repository. Attribute every remote image with publisher and source-page link.
- Do not use Pinterest, fan reposts, shopping replicas, or AI-generated Jennie lookalikes when an official or reputable editorial image is available.
- Treat stage costumes as amplified styling evidence, not as clothing reserved for celebrities. Match them to the user's actual scene—such as beach, nightlife, festival, date, travel, or everyday life—and preserve high exposure or drama when requested. Adjust exposure, heel height, or volume only for stated preference, movement, weather, dress code, or fit reasons. Cold weather is a thermal constraint, not a modesty judgment: separate the indoor/destination look from the transit layer before reducing the requested styling intensity.
- Avoid “显瘦遮肉,” “身材缺陷,” “梨形/苹果形,” and value judgments. Use neutral fit language such as “腰部余量较多” or “上身量感集中.”
- Never infer health, ethnicity, age, pregnancy, disability, or attractiveness from a photo.
- Recommend tailoring or fit checks when precision matters; do not present the result as professional patternmaking advice.
- When current or newly requested looks matter, browse and cite sources rather than relying only on the bundled snapshot.

## Corpus utilities

Validate the bundled research data:

```bash
python3 scripts/validate_corpus.py references/look-corpus.jsonl
python3 scripts/validate_visual_index.py references/visual-index.jsonl references/look-corpus.jsonl
python3 scripts/validate_evidence_clusters.py references/style-evidence-clusters.json references/look-corpus.jsonl
python3 scripts/select_visuals.py summary --variant 0
python3 scripts/select_visuals.py report
```

Build a neutral adaptation summary from a saved questionnaire response:

```bash
python3 scripts/profile_style_needs.py profile.json
```

The script output is a decision aid, not the final prose. Add context and explain the styling logic.
