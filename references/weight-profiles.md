# GEO Weight Profiles

Read this reference before selecting or changing the 100-point scoring model.

## Default profiles

Weights are percentages and each profile totals 100.

| Dimension | BRAND | LOCAL / RESTAURANT | B2B | PRODUCT | PERSON |
|---|---:|---:|---:|---:|---:|
| 实体清晰度 | 15 | 10 | 10 | 10 | 15 |
| 知识完整度 | 15 | 10 | 15 | 20 | 15 |
| 权威与证明 | 15 | 5 | 20 | 10 | 20 |
| 第三方信任 | 10 | 20 | 10 | 15 | 15 |
| AI 可见度 | 15 | 15 | 10 | 15 | 15 |
| AI 推荐力 | 15 | 20 | 10 | 15 | 10 |
| 竞争占位 | 10 | 10 | 10 | 10 | 5 |
| 跨平台一致性 | 5 | 10 | 5 | 5 | 5 |
| 商业证明 | — | — | 10 | — | — |

`RESTAURANT` maps to the `LOCAL_V1` profile. A multi-identity entity uses one primary profile and adds secondary-type questions to its query universe.

## Score calculation

Each dimension has a documented raw score from 0 to 100 and an evidence-backed rationale.

```text
dimension contribution = raw score × dimension weight / 100
overall GEO score = sum of all dimension contributions
```

The renderer recalculates both values. Do not hand-enter a final score that conflicts with the model.

## Raw-score evidence

Use the strongest available evidence for each dimension:

- Entity clarity: canonical name, aliases, organization/product/person relationships, structured data, POI consistency.
- Knowledge completeness: coverage of the attributes and questions required for the entity type.
- Authority and proof: first-party evidence, public institutions, standards, recognized experts, credible cases.
- Third-party trust: independent reviews, reputable media, marketplaces, communities, complaint/risk signals.
- AI visibility: weighted S3–S5 results across the query universe.
- AI recommendation: weighted S4–S5 results and whether a recommendation reason is present.
- Competitive position: weighted S2 loss rate, rank, share of recommendation set, and direct competitor evidence.
- Cross-platform consistency: agreement in facts, recommendation reasons, and citations across observed platforms.
- Commercial proof for B2B: named cases, implementation method, measurable outcomes, buyer proof, and disclosed assumptions.

Do not calculate a raw score from unavailable evidence. Mark the input `UNKNOWN`, disclose the limitation, and either exclude it with a renormalized model or use an explicitly labeled proxy.

## Preserving an existing report

When redesigning an existing report, preserve its documented scoring model and name it with a suffix such as `BRAND_V1_PRESERVED`. Show every original weight and rationale. Do not silently replace the original score with a default profile.

Use a default profile for a new diagnosis. Change it only when the entity’s economics or stated goal materially differ, and explain the change in `scoring_model.basis`.
