# 豆包“应用生成”版使用说明

## 大众用户：只需一个 ZIP

1. 在 GitHub 下载 [`jennie-style-decoder-doubao-app.zip`](jennie-style-decoder-doubao-app.zip)。
2. 打开豆包，新建对话并选择内嵌的“应用生成”技能。
3. 上传这个 ZIP。
4. 发送下面这一句话：

```text
请完整读取压缩包，严格按 SKILL.md 和 APP_BUILD_SPEC.md，直接交付其中已完成的单页 HTML 应用；不要总结，不要缩减 52 套数据，不要重写选图逻辑。
```

5. 豆包完成后，直接打开网页预览。用户不需要单独上传图片、JSON 或代码。

## 这版解决了什么

- 52 套造型全部作为可选记录内嵌进单页 HTML，而不是只给模型一段长提示词。
- 单次审美地图和个性化方案同时对 `lookId`、非空图片 URL 做硬去重。
- 最近出现的 24 套记录保存在浏览器本地，下一轮会降权；“换一批”不再永远取数组前五项。
- 三套个性化公式的主参考来自三种不同搭配机制。
- 远程图片失败时只降级为同一套造型的结构卡和来源链接，不拿某张常用图重复补位。
- 单选项再次点击可以取消；提交按钮直接生成第 3 步。

## 图片边界

项目不打包 Jennie 或媒体图片文件。52 套记录中，13 套使用带出处的稳定远程图；其余 39 套用“造型结构卡＋原始来源链接”进入轮换。因此网页能真正使用全部 52 套搭配证据，又不会谎称拥有 52 个稳定图片直链。

## 开发者更新样本

更新主语料或稳定视觉索引后运行：

```bash
python3 adapters/doubao/scripts/build_app_bundle.py
python3 adapters/doubao/scripts/validate_app_bundle.py
```

构建脚本会同步生成 `app-skill/references/looks.json`、内嵌数据的单页 HTML 和供大众下载的 ZIP。不要手工维护三份重复数据。

## 备用路径

[`JENNIE_STYLE_DECODER_DOUBAO.md`](JENNIE_STYLE_DECODER_DOUBAO.md) 是纯对话备用版；在你明确使用豆包“应用生成”技能时，应优先上传 ZIP。
