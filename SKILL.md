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
3. Collect current public evidence. For scoring, query design, entity-specific modules, and problem-to-asset mapping, read [references/diagnostic-method.md](references/diagnostic-method.md).
4. Classify every material claim. Before writing findings, read [references/evidence-policy.md](references/evidence-policy.md). Never describe simulated or inferred platform behavior as an observed test.
5. Build the structured report data using [references/data-contract.md](references/data-contract.md). Preserve conflicting source claims and supplied scores; do not silently normalize them.
6. Resolve report style before rendering. If the user has not already selected a style or delegated the choice, present the four options from [references/report-styles.md](references/report-styles.md) and wait for one answer. Style affects presentation only.
7. Render HTML:

```bash
python3 scripts/render_report.py input.json output.html
```

8. Verify the output: all required sections are present; evidence labels are visible; no horizontal page overflow at 390 px; print preview is legible; and the output makes no external network requests.

## Style selection contract

Use this compact prompt after diagnosis data exists and before HTML generation:

> 请选择报告风格：A 董事会咨询风（推荐）｜B 科技战略风｜C 品牌研究风｜D 数据分析风。若由我决定，请回复“自动选择”。

Do not ask again when the user already chose A–D, named an equivalent style, supplied a brand template, or explicitly requested automatic selection.

## Required output

- Executive summary with a decision-oriented verdict.
- KPI strip and weighted score dimensions.
- AI-search results with query state and evidence state.
- Competitor comparison and gap interpretation.
- P0–P3 issue register.
- Opportunity map based on business value and feasibility.
- 30/60/90-day roadmap with asset-oriented actions.
- Method, evidence, and limitation disclosures.
- Self-contained downloadable HTML; include the input JSON when reproducibility is useful.

## Quality guardrails

- Prefer verified absence or `UNKNOWN` to fabricated completeness.
- Do not promise a ranking or a fixed improvement date; express targets as hypotheses to test.
- Keep user-supplied facts and conclusions unchanged unless the user asks for re-research.
- Use tables for exact comparison, not decorative card grids.
- Keep body text near 16 px, use one accent color, ample whitespace, and restrained visual hierarchy.

