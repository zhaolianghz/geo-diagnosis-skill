# Report Data Contract

The renderer consumes a UTF-8 JSON object. See `examples/jinge-esports.json` for a complete working example.

## Required top-level fields

| Field | Type | Meaning |
|---|---|---|
| `report_title`, `entity`, `date`, `grade`, `executive_summary` | string | Report identity and decision summary |
| `style` | `A` \| `B` \| `C` \| `D` | Selected visual style |
| `score` | number 0–100 | Overall GEO score |
| `kpis` | array | `{label, value, note}` |
| `score_dimensions` | array | `{name, score, max, evidence}` |
| `search_performance` | object | `{disclaimer, evidence_state, rows}` |
| `competitors` | array | `{name, score, position}` |
| `issues` | array | `{priority, title, impact, action, evidence}` |
| `opportunities` | array | `{name, value, gap, feasibility, priority, note}` with 1–5 numeric axes |
| `roadmap` | array | `{window, theme, target, actions}` |
| `evidence_summary` | array | `{state, definition, count}` |
| `limitations` | array of strings | Scope and uncertainty disclosure |

`search_performance.rows` contains `{query, category, status, rank, coverage, finding}`. Use `Preferred`, `Recommended`, `Mentioned`, `Competitor Won`, `Not Found`, or `Unresolved` for `status`.

Optional fields include `entity_aliases`, `entity_type`, `industry`, `scope`, `version`, `purpose`, and `benchmark`.

## Invariants

- Every `score_dimensions[].score` is less than or equal to `max`.
- Overall score must equal the documented scoring model, not an average invented by the renderer.
- Evidence is one of `OBSERVED`, `VERIFIED`, `INFERRED`, or `UNKNOWN`.
- Opportunity axis values are integers from 1 to 5.
- Data is plain text. The renderer escapes all fields and does not accept embedded HTML.

## CLI

From the skill directory:

```bash
python3 scripts/render_report.py examples/jinge-esports.json report.html
```

The script exits non-zero with a readable message when required fields are missing or invalid.

