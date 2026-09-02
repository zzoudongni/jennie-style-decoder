# Body and styling questionnaire

Use the quick version by default. It has three short groups and nine questions. Tell users that approximate answers, multiple choices, and “不确定” are valid. For preference grids, users only need to mark the items they have a clear opinion about.

## Presentation rule

Do not default to a long numbered text questionnaire that requires users to copy option codes.

1. In a client with inline interactive HTML, use `assets/profile-form.html`. Copy it to the task-owned visualization directory before displaying it. The user should be able to click controls and submit the result back into the conversation.
2. Preserve the nine-question data model, but reveal it as three compact visual groups rather than one dense wall of text.
3. Leave preference rows optional; blank means “no strong preference.”
4. If interactive HTML is unavailable, use the compact checkbox fallback below. Accept checked text directly and normalize it yourself; never ask the user to translate the choices into A/B/C codes.
5. Make every optional single-choice row clearable. A user who clicks the selected “经常穿 / 愿意尝试 / 不考虑” option again must return that row to the unanswered state; do not trap an accidental selection.

### Compact checkbox fallback

```markdown
身高：[填写]

成衣反馈（勾选符合项）
- [ ] 上衣肩合适、胸口偏紧
- [ ] 上衣肩或腰偏松
- [ ] 上衣肩紧
- [ ] 袖长常不合适
- [ ] 上衣容易堆量
- [ ] 裤子臀部合适、腰松
- [ ] 裤子腰合适、臀腿紧
- [ ] 裆部容易不适
- [ ] 裤长常不合适

目标与场景（各选需要项）
- 目标：[ ] 腿部线条利落  [ ] 上身轻盈  [ ] 腰线明确  [ ] 臀腿从容  [ ] 肩部存在感  [ ] 曲线  [ ] 干净线条  [ ] 只学逻辑
- 场景：[ ] 通勤上学  [ ] 日常旅行  [ ] 约会聚会  [ ] 海岛度假  [ ] 夜店派对  [ ] 演出音乐节  [ ] 正式活动
- 当天体感：( ) 炎热  ( ) 温和  ( ) 寒冷  ( ) 不确定
- 活动环境：( ) 全程室内  ( ) 室内为主·短暂室外  ( ) 室内外各半  ( ) 室外为主  ( ) 不确定
- 强度：( ) 克制  ( ) 灵活  ( ) 大胆

大胆元素与材质
对有明确感觉的项目，直接勾选“常穿／想试／不考虑”；未勾选视为无强偏好。

当前与目标风格
- 当前：[ ] 极简  [ ] Chill  [ ] 机能  [ ] 浪漫  [ ] 性感  [ ] 街头  [ ] 经典  [ ] 混搭
- 目标：[ ] 极简  [ ] Chill  [ ] 机能  [ ] 浪漫  [ ] 性感  [ ] 街头  [ ] 经典  [ ] 混搭
```

## Quick version

### A. 成衣穿着反馈

1. **身高**：____ cm

2. **买合身上衣或短外套时，最常见的情况是？** Choose all that apply.
   - 肩合适，但胸口偏紧
   - 胸口合适，但肩或腰偏松
   - 肩部经常偏紧
   - 袖子经常偏长 / 偏短
   - 上衣容易显得厚重或堆在身上
   - 基本没有固定问题
   - 不确定

3. **买合身长裤时，最常见的情况是？** Choose all that apply.
   - 腰合适，但臀部或大腿偏紧
   - 臀部合适，但腰围偏松
   - 裆部容易紧、卡或下坠
   - 裤长经常偏长 / 偏短
   - 基本没有固定问题
   - 不确定

4. **连衣裙或连体裤标出的腰线通常落在哪里？**
   - 比我的自然腰更高
   - 大致在自然腰
   - 比自然腰更低
   - 不确定
   - 很少穿这类衣服

5. **这次最想改善什么？** Choose at most two.
   - 让整体更利落、腿部视觉更修长
   - 减少上半身的厚重感
   - 让腰线更明确
   - 让臀腿线条更从容
   - 增加肩部存在感
   - 增加曲线感
   - 让整体线条更干净
   - 暂时不修饰身材，只学习 Jennie 的搭配逻辑

### B. 场景与大胆程度

6. **这次具体想穿去哪里？可多选，也可以自己写得很细。**
   - 通勤 / 上学
   - 日常休闲 / 城市旅行
   - 约会 / 聚会
   - 海岛 / 泳池 / 度假
   - 夜店 / 派对
   - 演出 / 音乐节
   - 正式活动
   - 其他：____

   同时各点一下，不用新增步骤：
   - **当天体感：**炎热 / 温和 / 寒冷 / 不确定
   - **主要活动环境：**全程室内 / 室内为主、短暂室外 / 室内外各半 / 室外为主 / 不确定

季节名称只是提示；优先按真实气温、风雨、室外停留时间和目的地条件判断。寒冷通勤与室内约会应拆成“途中外层 + 目的地造型”，不要自动把室内高露肤方案改成保守版。

7. **这次想要的整体表达强度是什么？**
   - 克制：更偏好完整覆盖或安静造型
   - 灵活：根据场景决定，可以安静也可以大胆
   - 大胆：希望保留 Jennie 造型原本的戏剧性与露肤度

   再从下面挑出你有明确感觉的元素，分别标记：**A 经常穿 / B 愿意尝试 / C 这次不考虑**。不需要逐项回答。

   - 低胸或深领口
   - 低腰裤 / 低腰裙
   - 抹胸
   - 吊带 / 细肩带
   - 露腰短上衣
   - 露背
   - underwear-as-outerwear
   - 蕾丝或透视纱
   - 超短下装或高开衩
   - 长靴
   - 多层腰带、腰封或明显五金
   - 其他：____

“大胆”不会触发自动降级版本；系统应先给同等强度方案。任何身材都可以选择上述元素，具体建议只处理版型、固定方式和场景需求。

### C. 你现有的衣橱语言

8. **你平时最常穿什么材质？又愿意增加什么材质？** 分成两组多选：**A 衣橱里经常穿 / B 目前少穿但愿意尝试**。

   - 纯棉 / T恤面料
   - 针织
   - 牛仔
   - 速干、尼龙或运动机能面料
   - 亚麻
   - 缎面或丝感面料
   - 蕾丝
   - 透视纱 / 网纱
   - 皮革或皮革感材质
   - 麂皮或麂皮感材质
   - 羽毛、流苏或毛绒质感
   - 其他：____

9. **你现在的穿衣风格，以及想靠近的方向分别是什么？** 两组各选1–3项。

   - 极简基础
   - 休闲慵懒 / chill
   - 运动机能
   - 女性化 / 浪漫
   - 性感大胆
   - 酷感 / 街头
   - 经典精致
   - 实验性混搭
   - 不确定

## Optional precise version

Only request these if the user wants more precise proportion guidance:

- 胸围：软尺绕胸部最丰满处一周，贴合但不勒。
- 自然腰围：身体自然站立，绕躯干最窄处一周；若不明显，先向一侧弯腰，以形成折痕处为参考。
- 臀围：双脚自然并拢，绕臀部最丰满处一周。
- 自然腰到地面：赤脚直立，从自然腰侧面垂直量到地面。

Use centimeters. Accept missing fields. Ask the user to remeasure only when a number appears impossible or a tape path was clearly misunderstood.

## Handling photos

A photo is optional. If provided, request a neutral standing photo in fitted but non-compressive clothing, ideally front and side, only if the user is comfortable. Never require face visibility. Explain that lens, pose, clothing, and camera height can distort proportions.

Describe observable garment behavior, not body worth. Examples:

- Good: “这件上衣的肩缝落在肩点外侧，视觉量感集中在上半身。”
- Avoid: “你肩宽，所以不能穿……”
- Good: “目前证据不足以判断裤腰位置，先用你提供的穿着体验作为依据。”
- Avoid: estimating bust/waist/hip numbers from an image.

## Normalized input schema

```json
{
  "height_cm": 165,
  "top_fit": ["shoulder_ok_chest_tight"],
  "pants_fit": ["hips_ok_waist_loose"],
  "garment_waist_position": "at_natural_waist",
  "goals": ["cleaner_lines", "defined_waist"],
  "scenario": ["nightlife", "island_holiday"],
  "temperature_context": "cold",
  "wear_environment": "indoor_brief_outdoor",
  "exposure": "high",
  "intensity": "bold",
  "element_preferences": {
    "low_rise": "often_wear",
    "camisole": "often_wear",
    "low_neckline": "willing_to_try",
    "underwear_as_outerwear": "willing_to_try",
    "sheer": "willing_to_try"
  },
  "current_materials": ["cotton", "denim", "knit"],
  "open_to_materials": ["lace", "sheer_mesh", "leather", "suede"],
  "current_style": ["casual_chill", "minimal_basics"],
  "target_style": ["bold_sexy", "experimental_mix"],
  "measurements_cm": {
    "bust": null,
    "waist": null,
    "hip": null,
    "waist_to_floor": null
  },
  "notes": ""
}
```

Allowed values are documented in `scripts/profile_style_needs.py --show-schema`.
