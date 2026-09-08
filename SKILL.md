---
name: geo-diagnosis
description: Use when a user asks to diagnose a company, brand, product, person, restaurant, store, or local business for GEO, generative search, AI visibility, AI recommendations, AI Share of Voice, competitor presence, or a client-ready GEO diagnosis report.
---

# GEO Diagnosis

## Overview

Produce an evidence-backed diagnosis of how an entity is understood and recommended by generative search. Separate facts from inference, turn gaps into prioritized assets and actions, and render a professional HTML report only after the report style is resolved.

## Workflow

1. Establish the entity boundary from its name and any supplied website, city, files, or aliases. Identify one primary type and any secondary types: BRAND, B2B, LOCAL, RESTAURANT, PRODUCT, PERSON, or UNKNOWN.
2. Infer the commercial goal from context: BRAND, LEAD, LOCAL, SALES, FRANCHISE, B2B, REPUTATION, or EXPERT. Ask one question only when ambiguity would materially change the query universe or scoring.
3. Build the query universe. Read [references/query-universe.md](references/query-universe.md). A full diagnosis uses 20–50 exact user questions and must show their clusters, intent, stage, business value, question weight, current state, evidence, and proposed asset. Use 8–12 only for an explicitly requested quick scan.
4. Select the primary entity weight profile. Read [references/weight-profiles.md](references/weight-profiles.md), disclose every weight, and keep the applied profile stable for retests. When redesigning an existing report, preserve its original documented score model instead of silently replacing it.
5. Collect current public evidence. For entity-specific modules, competitors, opportunities, and problem-to-asset mapping, read [references/diagnostic-method.md](references/diagnostic-method.md).
6. Classify every material claim. Before writing findings, read [references/evidence-policy.md](references/evidence-policy.md). Never describe simulated or inferred platform behavior as an observed test.
7. Build the structured report data using [references/data-contract.md](references/data-contract.md). Every material gap must map to a quantified asset with format, quantity, channel, owner, validation question, and success metric. Preserve conflicting source claims and supplied facts.
8. Resolve report style before rendering. If the user has not already selected a style or delegated the choice, present the four options from [references/report-styles.md](references/report-styles.md) and wait for one answer. Style affects presentation only.
9. Render HTML. The renderer invokes the deterministic diagnosis engine, recalculates scores, question-weighted KPI values, and opportunity scores, and rejects invalid inputs:

```bash
python3 scripts/render_report.py input.json output.html
```

10. Verify the output: all required sections are present; the full query inventory and applied weights are visible; evidence labels are visible; no horizontal page overflow at 390 px; print preview is legible; and the output makes no external network requests.

## Style selection contract

Use this compact prompt after diagnosis data exists and before HTML generation:

> 请选择报告风格：A 董事会咨询风（推荐）｜B 科技战略风｜C 品牌研究风｜D 数据分析风。若由我决定，请回复“自动选择”。

Do not ask again when the user already chose A–D, named an equivalent style, supplied a brand template, or explicitly requested automatic selection.

## Required output

- Executive summary with a decision-oriented verdict.
- KPI strip calculated from the row-level question inventory.
- Applied scoring profile, dimension weights, raw-score rationale, and weighted contributions.
- Full 20–50 question inventory with query weight, state, evidence, and suggested asset.
- Condensed AI-search results with query state and evidence state.
- Competitor comparison and gap interpretation.
- P0–P3 issue register.
- Opportunity map based on business value and feasibility.
- Quantified content and knowledge-asset blueprint.
- 30/60/90-day roadmap with asset-oriented actions.
- Claim-level evidence registry plus method and limitation disclosures.
- Self-contained downloadable HTML; include the input JSON when reproducibility is useful.

## Quality guardrails

- Prefer verified absence or `UNKNOWN` to fabricated completeness.
- Never invent keyword search volume. Use explicit business weights or the disclosed business-value normalization fallback.
- Do not promise a ranking or a fixed improvement date; express targets as hypotheses to test.
- Keep user-supplied facts and conclusions unchanged unless the user asks for re-research.
- Use tables for exact comparison, not decorative card grids.
- Keep body text near 16 px, use one accent color, ample whitespace, and restrained visual hierarchy.
