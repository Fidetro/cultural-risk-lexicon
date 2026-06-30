# 中文文化与历史风险关联库

这是一个以 Codex skill 为优先形态、以公开来源支撑的中文文化与历史风险关联库，用于辅助复核中文文本中可能出现的历史伤痛、侵华战争、战犯人物、部队番号和重大事件日期关联。

第一版种子数据聚焦日本侵华相关条目：战争罪行实体、相关人物、军事部队和重大事件日期。它面向人工复核流程，不用于自动审查，也不替代最终内容判断。

## 能做什么

- 将词条、别名、数字写法、拼音写法和常见近似误写关联到风险实体。
- 返回简短说明、风险类别、置信度和来源链接。
- 支持 `731`、`0731`、`七三一`、`713`、`严颂`、`yansong` 等案例。
- 在 `skills/cultural-risk-lexicon` 下提供可直接复用的 Codex skill。

## 不做什么

- 不判断内容是否违反平台政策。
- 不推断用户主观意图。
- 不替代人工历史语境复核。
- 不收录没有公开来源支撑的条目。

## 快速开始

```bash
python3 scripts/query.py 731
python3 scripts/query.py 713
python3 scripts/query.py 严颂
python3 scripts/query.py yansong --json
python3 scripts/query.py 1937-12-13
```

## 示例输出

```text
可能关联：七三一部队 / Unit 731
匹配：713 -> 713 (listed-near-match)
风险类别：japanese-war-crimes, biological-warfare, historical-trauma
置信度：0.90
复核说明：数字近似、顺序错位或实验部队语境中出现时，可能被中文读者联想到七三一部队，建议结合上下文人工复核。
```

## Codex Skill 用法

在 Codex 环境中复制或引用 `skills/cultural-risk-lexicon`。该 skill 会指导 Codex 在解释可疑词、数字编号、拼音别名或历史日期之前，先调用 `scripts/query.py` 查询本地数据。

## 数据格式

条目位于 `data/entities.json` 和 `data/events.json`。为保持 CLI/API 兼容，JSON 字段名使用英文；展示内容和说明文字优先使用中文。

```json
{
  "id": "entity-unit-731",
  "canonical": "七三一部队 / Unit 731",
  "type": "military_unit",
  "aliases": ["731", "0731", "七三一", "七三一部队"],
  "risk_categories": ["japanese-war-crimes", "biological-warfare"],
  "review_note": "作为编号、日期形态或实验部队语境出现时，建议人工复核。",
  "sources": ["https://www.1937china.com/"]
}
```

## 来源策略

种子数据优先使用稳定公开来源：国家公祭网、纪念馆/博物馆官网、中国人民抗日战争纪念馆或中国抗战胜利网、国家档案馆/档案局、全国人大/中国政府网、人民网/新华网、审判文书、权威百科和学术资料。每个条目至少需要一个来源链接。

如果暂时找不到稳定的一手页面，可以保留可靠百科或英文来源作为补充，但应继续优先替换为更权威的中文来源。

## 许可证

MIT
