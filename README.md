# GEO Diagnosis Skill

一个面向企业、品牌、产品、人物、餐饮门店和本地商业的 GEO（Generative Engine Optimization）诊断 Skill。

它用于分析一个实体在生成式搜索中的认知度、可见度与推荐能力，将证据、竞品差距和内容缺口转化为可执行的 GEO 增长方案，并生成可直接交付客户的单文件 HTML 报告。

## 核心能力

- 自动识别 `BRAND`、`B2B`、`LOCAL`、`RESTAURANT`、`PRODUCT`、`PERSON` 等实体类型。
- 推断品牌认知、获客、到店、销售、加盟、B2B 和口碑等商业目标。
- 建立品牌认知、品类推荐、地域、人群、场景、比较和商业决策问题集。
- 区分 `Not Found`、`Competitor Won`、`Mentioned`、`Recommended` 和 `Preferred`。
- 输出 GEO 评分、竞品对比、P0–P3 问题优先级、机会地图及 30/60/90 天路线图。
- 将每个问题映射为实体页、FAQ、案例、白皮书、场景内容和第三方信任资产。
- 支持四种专业报告视觉风格，生成响应式、可打印、无外部依赖的 HTML。

## 报告风格

Skill 会在生成 HTML 前让用户选择风格；如果用户已经指定或要求自动选择，则不会重复询问。

| 代码 | 风格 | 适用场景 |
|---|---|---|
| A | 董事会咨询风 | 客户交付、高管汇报、战略诊断 |
| B | 科技战略风 | AI、科技与数字化转型项目 |
| C | 品牌研究风 | 品牌、市场与消费者洞察 |
| D | 数据分析风 | 内部运营分析与复盘 |

视觉风格只改变版式与配色，不改变事实、评分、证据标签或核心结论。

## 证据规则

报告中的重要判断必须标记证据状态：

| 状态 | 含义 |
|---|---|
| `OBSERVED` | 本次任务中直接取得的页面、文件、平台回答或截图 |
| `VERIFIED` | 已由可靠公开来源确认的事实 |
| `INFERRED` | 根据公开资料、内容覆盖或代理指标得出的推断 |
| `UNKNOWN` | 数据不足、来源冲突或暂时无法验证 |

没有实时取得的平台回答不得写成“实测”。无法验证的数据不会为了让报告显得完整而被虚构。

## 安装

将仓库克隆到 Codex skills 目录：

```bash
git clone https://github.com/zhaolianghz/geo-diagnosis-skill.git ~/.codex/skills/geo-diagnosis
```

重新打开 Codex 会话后，通过 `$geo-diagnosis` 显式调用，也可以让 Codex 根据 GEO、AI 搜索可见度或 GEO 报告请求自动发现该 Skill。

## 使用示例

```text
$geo-diagnosis 帮我诊断“竞鹅电竞酒店”在 AI 搜索中的表现，并生成客户交付版 HTML 报告。
```

也可以补充官网、城市、商业目标、竞品或内部资料：

```text
$geo-diagnosis 诊断杭州某餐厅，目标是提升“西湖附近聚餐餐厅推荐”的 AI 到店曝光。报告用于老板汇报，自动选择风格。
```

## 生成 HTML

仓库提供了一个仅依赖 Python 标准库的确定性渲染器：

```bash
python3 scripts/render_report.py examples/jinge-esports.json report.html
```

输入数据结构见 [`references/data-contract.md`](references/data-contract.md)，完整示例见 [`examples/jinge-esports.json`](examples/jinge-esports.json)。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖必需报告章节、视觉风格切换、HTML 转义、移动端与打印样式、缺失字段、评分边界、机会坐标和证据状态验证。

## 目录结构

```text
geo-diagnosis/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── report.css
├── examples/
│   └── jinge-esports.json
├── references/
│   ├── data-contract.md
│   ├── diagnostic-method.md
│   ├── evidence-policy.md
│   └── report-styles.md
├── scripts/
│   └── render_report.py
└── tests/
    └── test_render_report.py
```

## 方法边界

- AI 推荐结果会随时间、地区、账户状态和模型版本变化。
- 评分必须说明数据范围与权重，缺失数据不得参与计算。
- 路线图目标是待复测的增长假设，不是排名或商业结果承诺。
- Skill 不会自动获得需要登录、付费或人工授权的平台数据。

