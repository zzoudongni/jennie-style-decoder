---
name: jennie-style-decoder-doubao-app
description: 在豆包的“应用生成”技能中，交付一个可直接运行的 Jennie Style Decoder 单页 HTML；使用内置 52 套造型数据、强制去重与跨轮轮换，为用户生成三步式视觉审美报告和个性化穿搭转译方案。
---

# Jennie Style Decoder · 豆包应用生成版

当用户上传本压缩包时，目标是交付一个可运行的单页 HTML 应用，不是总结附件，也不是重新设计一个缩水版。

## 执行顺序

1. 完整读取 `APP_BUILD_SPEC.md`。
2. 将 `assets/JENNIE_STYLE_DECODER_APP.html` 作为交付基线。它已内嵌 52 套造型数据与完整 JavaScript，不依赖本地文件、Python、框架或构建工具。
3. 优先原样交付该 HTML；如果豆包必须重新生成页面，必须保留规范中的数据与硬性不变量。
4. `references/looks.json` 只用于核对 52 套数据，不应改成仅有 5–13 套的小数组。

## 不得删除的功能

- 三步路径：一页审美地图 → 勾选资料 → 个性化视觉转译。
- 52 个唯一 `lookId`。
- 同一结果中 `lookId` 与非空 `imageUrl` 双重去重。
- 最近 24 个造型的 `localStorage` 跨轮轮换。
- “换一批参考”和“换一组方案”按钮。
- 图片加载失败时，在原造型位置显示来源链接与结构卡，不换成已出现的旧图。
- 低腰、高露肤、内衣外穿不因“普通人”身份自动降级。
- 寒冷天气拆分途中外层与目的地造型。

## 交付

最终只需向用户提供可点击预览和可下载的 `JENNIE_STYLE_DECODER_APP.html`。不要要求用户另外上传图片、JSON 或脚本。
