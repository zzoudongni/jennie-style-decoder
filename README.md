# Jennie Style Decoder

一个把 Jennie Kim 近两年穿搭提炼为“可解释、可学习、可迁移”规则的开源 Codex Skill。

它做两件事：

1. 基于带来源的机场/私服、舞台和正式活动样本，输出“参考图＋视觉标注＋搭配结论”的 Jennie 时尚审美报告。
2. 根据用户真实的衣服合身体验、具体场景、季节体感与室内外环境、偏爱的露肤元素、常穿材质及目标风格，为三套穿搭公式分别匹配2–3张 Jennie 参考图并生成同等强度或按需变化的转译方案。

它不做虚拟试穿，不要求购买同款，不使用混乱的中国女装尺码，也不把用户分类为“梨形/苹果形”。

## 最简单的使用路径

1. 默认先看一页式 Jennie 审美地图：6 个特点、6–8 张动态选择的代表图。需要研究细节时再展开完整证据报告；完整模式仍为每个特点提供 3–5 张造型图和一张反例。
2. 通过可直接勾选的三组表单回答 9 个问题；无需复制选项编号。精确围度为可选项。问卷会区分“经常穿／愿意尝试／这次不考虑”的低腰、低胸、抹胸、吊带、蕾丝、皮革等元素。
3. 获得 Keep / Adjust / Avoid、三套带 Jennie 逻辑与试穿检查的穿搭公式，以及配色、配饰、妆发、材质和 7 天审美练习。

参考图不是每次固定重复：豆包公开测试包内嵌 53 张低分辨率分析参考图，覆盖 45 套不同造型组；每次依据场景与用户资料动态选择，同一页对造型和图片双重去重。研究语料仍保留 52 条造型记录，不把“53 张照片”误写成“53 套造型”。

“普通人”不会触发自动保守化：如果用户喜欢真实低腰、underwear-as-outerwear、透视纱或高露肤，系统会先输出同等强度方案，再只按明确的场景、活动、固定方式、天气或个人要求提供变化版本。

## 安装到 Codex

将仓库克隆或下载后，把 `.agents/skills/translate-jennie-style` 保持原结构放入项目中。然后在 Codex 中使用：

```text
Use $translate-jennie-style to explain Jennie's styling system and create my personalized plan.
```

也可以直接说：

```text
请用 $translate-jennie-style，先给我精简的 Jennie 审美报告，再问我必要的身材与场景问题。
```

## 在豆包“应用生成”中使用

大众用户只需要上传一个 ZIP：

1. 下载 [`adapters/doubao/jennie-style-decoder-doubao-app.zip`](adapters/doubao/jennie-style-decoder-doubao-app.zip)。
2. 在豆包新建对话并选择内嵌的“应用生成”技能。
3. 上传 ZIP，然后发送：`请完整读取压缩包，严格按 SKILL.md 和 APP_BUILD_SPEC.md，直接交付其中已完成的单页 HTML 应用；不要总结，不要缩减 52 套数据，不要重写选图逻辑。`
4. 打开豆包生成的网页预览即可使用。

ZIP 中已有一个内嵌完整数据、逻辑和低清分析参考图的单页 HTML；用户无需再上传图片、JSON、Python 或其他文件。网页在每次报告和方案中强制对 `lookId` 与 `assetId` 双重去重，并用本地历史记录跨轮轮换。

详细步骤与验收标准见 [`adapters/doubao/README.md`](adapters/doubao/README.md)。原来的 [`JENNIE_STYLE_DECODER_DOUBAO.md`](adapters/doubao/JENNIE_STYLE_DECODER_DOUBAO.md) 保留为纯对话备用版，不是“应用生成”首选入口。

## 目录

```text
.agents/skills/translate-jennie-style/
├── SKILL.md
├── agents/openai.yaml
├── assets/
│   └── profile-form.html
├── references/
│   ├── adaptation-rules.md
│   ├── body-questionnaire.md
│   ├── look-corpus.jsonl
│   ├── output-templates.md
│   ├── research-method.md
│   ├── sources.md
│   ├── style-findings.md
│   ├── style-evidence-clusters.json
│   ├── visual-index.jsonl
│   └── visual-output.md
└── scripts/
    ├── profile_style_needs.py
    ├── select_visuals.py
    ├── validate_corpus.py
    ├── validate_evidence_clusters.py
    └── validate_visual_index.py

adapters/doubao/
├── app-skill/
│   ├── SKILL.md
│   ├── APP_BUILD_SPEC.md
│   ├── README.md
│   ├── THIRD_PARTY_MEDIA.md
│   ├── assets/JENNIE_STYLE_DECODER_APP.html
│   └── references/local-visual-manifest.json
├── scripts/
│   ├── build_app_bundle.py
│   ├── build_local_visual_bundle.py
│   ├── audit_local_images.py
│   └── validate_app_bundle.py
├── app-template.html
├── jennie-style-decoder-doubao-app.zip
├── JENNIE_STYLE_DECODER_DOUBAO.md
└── README.md
```

## 验证数据

```bash
cd .agents/skills/translate-jennie-style
python3 scripts/validate_corpus.py references/look-corpus.jsonl
python3 scripts/validate_visual_index.py references/visual-index.jsonl references/look-corpus.jsonl
python3 scripts/validate_evidence_clusters.py references/style-evidence-clusters.json references/look-corpus.jsonl
python3 scripts/select_visuals.py summary --variant 0 --ids-only
python3 scripts/select_visuals.py report --ids-only
python3 scripts/profile_style_needs.py --show-schema
cd ../../../adapters/doubao
python3 scripts/validate_app_bundle.py
```

## 14 个工作日公开测试

- 测试观察期为 2026-09-07 至 2026-09-24，共 14 个工作日；测试期长度不构成版权授权或责任豁免。
- 测试期收集：豆包加载成功率、图片/造型重复率、轮换覆盖率、来源链接完整度和用户理解成本。
- 测试期结束时决定：补全来源、替换/移除有争议图片、改用授权素材，或转为用户自带图片的公开版。

## 研究边界

- 当前资料快照覆盖 2024-09-01 至 2026-08-31，精选 52 套造型，不等于 Jennie 完整衣橱。精确日未核实的记录只保留到月份，不虚构日期。
- 公开测试包中的图片已压缩为仅供分析辨识的低分辨率 WebP，只与具体穿搭评论和转译结论同页出现，不提供原始高清图库。图片仍属于各自权利人，不在本项目的开源许可证内。
- 品牌/单品识别来自已列出的官方内容或时尚媒体；搭配逻辑是基于样本的解释，应标注置信度。
- 后续若要求“最新一到两年”，应按当日重新计算时间窗并更新语料。

## 非关联声明

这是由粉丝视角出发的独立教育项目，与 Jennie Kim、OA Entertainment、BLACKPINK、YG Entertainment、Chanel 或文中品牌及媒体无隶属、赞助或背书关系。相关姓名、商标、文章和影像权利归各自权利人所有。

## 第三方媒体、来源与移除

项目不主张拥有 Jennie 照片的版权，也无权授权他人转载、销售或商业使用这些照片。照片仅为评论、研究、审美教育和造型转译而以压缩形式展示。如您是相关权利人，请通过 GitHub Issue 提出署名修正、来源修改或移除请求，维护者核实后将尽快处理。详细素材状态见豆包 ZIP 中的 `THIRD_PARTY_MEDIA.md`。

本声明不构成法律意见，也不代表对任何特定使用方式合法性的保证。

## License

代码与原创文字框架采用 [MIT License](LICENSE)。外部链接、品牌标识、人物姓名及第三方内容不因此获得重新授权。
