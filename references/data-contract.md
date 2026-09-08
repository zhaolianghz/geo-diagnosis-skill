# Report Data Contract

The renderer consumes a UTF-8 JSON object. Use `examples/jinge-esports.json` as the canonical complete example.

## Required top-level fields

| Field | Type | Meaning |
|---|---|---|
| `report_title`, `entity`, `date`, `grade`, `executive_summary` | string | Report identity and decision summary |
| `style` | `A` \| `B` \| `C` \| `D` | Selected report style |
| `scoring_model` | object | Applied scoring profile and weighted dimensions |
| `query_universe` | array | Full GEO search-question inventory and row-level results |
| `search_performance` | object | Condensed management view of representative searches |
| `competitors` | array | Direct competitor comparison |
| `issues` | array | P0–P3 issue register |
| `asset_blueprint` | array | Quantified problem-to-asset plan |
| `opportunities` | array | Opportunity inputs; score is calculated by the engine |
| `roadmap` | array | 30/60/90-day execution plan |
| `evidence_summary` | array | Definitions and counts by evidence state |
| `evidence_registry` | array | Claim-level source register |
| `limitations` | array of strings | Scope and uncertainty disclosure |

Optional identity fields include `entity_aliases`, `entity_type`, `industry`, `scope`, `version`, `purpose`, `benchmark`, `management_judgment`, and `competitive_summary`.

Legacy fields `score`, `kpis`, and `score_dimensions` may remain in an old dataset, but the renderer does not trust them. It recalculates score and KPI values from `scoring_model` and `query_universe`.

## Scoring model

```json
{
  "scoring_model": {
    "profile": "BRAND_V1",
    "basis": "Why this profile and these inputs apply",
    "dimensions": [
      {
        "name": "AI 可见度",
        "raw_score": 72,
        "weight": 15,
        "rationale": "Which evidence produced the raw score"
      }
    ]
  }
}
```

All dimension weights must total exactly 100. Each `raw_score` must be from 0 to 100. The engine calculates each `contribution = raw_score × weight / 100` and the final score as the sum of contributions.

## Query universe

Use 20–50 questions for a full diagnosis. A quick scan may use 8–12 only when the user asks for a quick scan.

```json
{
  "query": "杭州电竞酒店推荐",
  "cluster": "地域推荐",
  "intent": "比较选择",
  "goal": "LOCAL",
  "stage": "考虑",
  "state": "S2",
  "rank": null,
  "rank_label": "未进入推荐集",
  "coverage": "3/7",
  "evidence": "OBSERVED",
  "has_citation": false,
  "checked_facts": 2,
  "accurate_facts": 2,
  "business_value": 5,
  "competition": 5,
  "suggested_asset": "杭州门店场景页",
  "finding": "竞品被优先推荐"
}
```

An optional numeric `weight` may be supplied for every query; explicit weights must be positive and total 100. If no explicit weights exist, the engine derives `query_weight` by normalizing `business_value`. If neither exists, it uses equal weights. The chosen method is disclosed in the report.

Query states are `S0` through `S5`. Evidence is `OBSERVED`, `VERIFIED`, `INFERRED`, or `UNKNOWN`. `UNKNOWN` rows remain visible but are excluded from metric denominators.

The engine calculates:

- `AI visibility rate = weighted S3+S4+S5 / effective query weight`
- `AI recommendation rate = weighted S4+S5 / effective query weight`
- `Top-3 rate = weighted queries with rank ≤ 3 / effective query weight`
- `competitor-loss rate = weighted S2 / effective query weight`
- `citation coverage = cited recommendation weight / S4+S5 weight`
- `entity accuracy = accurate checked facts / all checked facts`

## Asset blueprint

Every material gap must map to an executable asset:

```json
{
  "priority": "P0",
  "problem": "Canonical entity is ambiguous",
  "asset": "Canonical brand entity page",
  "format": "Web page + Organization structured data",
  "quantity": "1 page",
  "channels": ["Official website", "knowledge platform", "POI"],
  "owner": "Brand + Engineering",
  "validation_queries": ["X 是什么？", "X 与旧名称是否为同一品牌？"],
  "metric": "Both questions reach S4+ and entity accuracy ≥95%"
}
```

Avoid unquantified actions such as “publish more content”. State the asset, quantity, channel, owner, validation question, and success metric.

## Opportunities

Each opportunity requires four integer inputs from 1 to 5:

```json
{
  "name": "场景推荐占位",
  "value": 5,
  "business_value": 5,
  "gap": 4,
  "feasibility": 3,
  "evidence_confidence": 4,
  "priority": "P1",
  "note": "Why it matters"
}
```

The engine calculates `opportunity_score` as business value 35% + gap 30% + feasibility 20% + evidence confidence 15%, normalized to 100.

For backward compatibility, `value` mirrors `business_value`; the current renderer validates it when present.

## Evidence registry

```json
{
  "id": "E01",
  "claim": "Fact or report judgment",
  "state": "VERIFIED",
  "source": "Source name",
  "url": "https://example.com/source",
  "date": "2026-09-07",
  "source_grade": "A",
  "supports": "The section, score, or conclusion supported"
}
```

Keep missing URLs visible as a limitation; do not promote an inherited source label to a current verification.

## Invariants

- Scoring weights total 100; all scores are within range.
- Explicit query weights are complete and total 100.
- Opportunity inputs are integers from 1 to 5.
- Evidence states use the four-state vocabulary exactly.
- Plain-text fields only. The renderer escapes all values and does not accept embedded HTML.
- Do not manually overwrite computed scores or computed KPI values.

## CLI

From the skill directory:

```bash
python3 scripts/render_report.py examples/jinge-esports.json report.html
```

The script exits non-zero with a readable message when required fields are missing or invalid.
