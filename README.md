# Jennie Style Decoder

一个把 Jennie Kim 近两年穿搭提炼为“可解释、可学习、可迁移”规则的开源 Codex Skill。

它做两件事：

1. 基于带来源的机场/私服、舞台和正式活动样本，输出“参考图＋视觉标注＋搭配结论”的 Jennie 时尚审美报告。
2. 根据用户真实的衣服合身体验、具体场景、季节体感与室内外环境、偏爱的露肤元素、常穿材质及目标风格，为三套穿搭公式分别匹配2–3张 Jennie 参考图并生成同等强度或按需变化的转译方案。

它不做虚拟试穿，不要求购买同款，不使用混乱的中国女装尺码，也不把用户分类为“梨形/苹果形”。

## 最简单的使用路径

1. 默认先看一页式 Jennie 审美地图：6 个特点、6–8 张动态选择的代表图。需要研究细节时再展开完整证据报告；完整模式仍为每个特点提供 3–5 张造型图和一张反例。
2. 通过可直接勾选的三组表单回答 9 个问题；无需复制选项编号。精确围度为可选项。问卷会区分“经常穿／愿意尝试／这次不考虑”的低腰、低胸、抹胸、吊带、蕾丝、皮革等元素。
3. 获得 Keep / Adjust / Avoid、三套穿搭公式和 7 天审美练习。

参考图不是每次固定重复：12套人工筛选的核心造型负责稳定质量，其余图片按百余套研究语料和原始来源动态补充。完整审美报告包含六个特点、31个图片位置，至少覆盖18套不同造型；个人方案中的每套公式配2–3张同机制参考图。

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

## 在豆包中使用

豆包不会直接执行 Codex Skill 的 Python、HTML 或目录依赖，因此不要把整个仓库 ZIP 当作可安装插件上传。仓库提供了一个不依赖代码的单文件兼容版：

1. 下载 [`adapters/doubao/JENNIE_STYLE_DECODER_DOUBAO.md`](adapters/doubao/JENNIE_STYLE_DECODER_DOUBAO.md)。
2. 在豆包网页版或电脑客户端的新对话中上传该 Markdown 文件。
3. 输入：`请完整阅读我上传的《JENNIE_STYLE_DECODER_DOUBAO.md》，把其中“给 AI 的最高优先级执行规则”作为本次任务规则。不要总结文件，直接开始 Jennie Style Decoder。`

详细步骤见 [`adapters/doubao/README.md`](adapters/doubao/README.md)。豆包版保留一页式审美报告、三组快速资料卡、场景/体感/室内外判断、真实低腰与高露肤优先规则、三套视觉转译公式和12套远程视觉锚点；无法运行的动态选图脚本被改写为文档内评分规则。

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
```

## 研究边界

- 当前资料快照覆盖 2024-09-01 至 2026-08-31，精选 31 套造型，不等于 Jennie 完整衣橱。
- 仓库只保存文字观察、来源链接、远程图片地址和转译结论，不下载或转载媒体图片文件；图片仍属于原始权利人，并在使用时链接回原文。
- 品牌/单品识别来自已列出的官方内容或时尚媒体；搭配逻辑是基于样本的解释，应标注置信度。
- 后续若要求“最新一到两年”，应按当日重新计算时间窗并更新语料。

## 非关联声明

这是由粉丝视角出发的独立教育项目，与 Jennie Kim、OA Entertainment、BLACKPINK、YG Entertainment、Chanel 或文中品牌及媒体无隶属、赞助或背书关系。相关姓名、商标、文章和影像权利归各自权利人所有。

## License

代码与原创文字框架采用 [MIT License](LICENSE)。外部链接、品牌标识、人物姓名及第三方内容不因此获得重新授权。
