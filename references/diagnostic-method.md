# Diagnostic Method

## Entity and goal routing

Allow multiple identities. A hotel chain can be `BRAND` + `LOCAL` + `B2B`; a restaurant can be `LOCAL` + `RESTAURANT`. Choose one primary type for scoring and use secondary types to add relevant query clusters.

Default goals when absent:

| Entity | Default goals |
|---|---|
| Restaurant or local service | LOCAL + REPUTATION |
| Consumer brand or product | BRAND + SALES |
| B2B company | B2B + LEAD |
| Chain business | BRAND + LOCAL + FRANCHISE |
| Person or expert | EXPERT + LEAD |

## Query universe

Build the complete question inventory using [query-universe.md](query-universe.md). Generate questions, not isolated keywords. Cover only commercially relevant clusters:

1. Entity recognition: “X 是什么？”
2. Category recommendation: “有哪些值得推荐的 Y？”
3. Geography: “城市/商圈 + Y 推荐”
4. Audience: “适合某类人群的 Y”
5. Scenario: “某场景应该选择什么？”
6. Comparison: “X 和竞品有什么区别？”
7. Commercial decision: price, ROI, cases, suppliers, franchise, procurement.
8. Trust and risk: reviews, complaints, qualifications, accuracy.

Use 20–50 questions for a full diagnosis and a stable baseline set for later retesting. For each result record appearance, first position, proactive recommendation, reason, citation, competitor, factual accuracy, question weight, and proposed asset. The report must display the whole inventory.

## Query states

| State | Meaning |
|---|---|
| S0 Unresolved | The category or intent was misunderstood |
| S1 Not Found | Category exists; neither the entity nor a direct competitor is recommended |
| S2 Competitor Won | A competitor is recommended while the entity is absent |
| S3 Mentioned | Entity appears but is not recommended |
| S4 Recommended | Entity enters the recommendation set |
| S5 Preferred | Entity is the first-priority recommendation |

Treat S2 as more urgent than S1: it indicates an occupied recommendation position rather than a simple content gap.

## Scoring

Use an explicit 100-point model and show the weights. Select the entity-specific profile from [weight-profiles.md](weight-profiles.md). The default BRAND model is:

| Dimension | Weight |
|---|---:|
| Entity assets | 15 |
| Knowledge completeness | 15 |
| Authority | 15 |
| Third-party trust | 10 |
| AI visibility | 15 |
| AI recommendation | 15 |
| Competitive strength | 10 |
| Information consistency | 5 |

Adjust weights by entity type: LOCAL emphasizes POI, reviews, geographic facts, and scenarios; B2B emphasizes cases, expertise, solution depth, authority, and commercial proof; PRODUCT emphasizes product facts, comparison, reviews, and purchase scenarios. Disclose the applied profile, every dimension weight, the raw score rationale, and each weighted contribution.

The engine calculates weighted visibility rate, recommendation rate, Top-3 rate, competitor-loss rate, entity accuracy, and citation coverage from the row-level question inventory. Calculate cross-AI consistency and AI Share of Voice only when multiple observed platform responses provide the required denominator. Do not calculate a metric from unavailable data.

## Competitors and opportunities

Choose 3–5 direct competitors using category, geography, price band, audience, and business model. State why each was selected.

For each opportunity score four inputs from 1–5: commercial value, current gap, feasibility, and evidence confidence. Plot value against feasibility; show gap and priority in the label. Do not imply the map is market-size research unless market data was actually obtained.

Calculate the opportunity score as commercial value 35% + gap 30% + feasibility 20% + evidence confidence 15%, normalized to 100.

## Problem-to-asset mapping

Every issue must produce a concrete asset or operating change:

- Entity ambiguity → canonical entity page, aliases, structured data, consistent POI records.
- Missing scenario recall → scenario landing page, FAQ cluster, expert content, user evidence.
- Competitor Won → differentiated positioning, comparative proof, third-party validation.
- Weak commercial proof → verified cases, methodology, financial model with assumptions.
- Weak authority → white paper, standards participation, expert authorship, credible media.

Prioritize P0 (≤7 days), P1 (≤30 days), P2 (31–90 days), and P3 (>90 days). Keep roadmap targets testable and non-guaranteed.

For every asset record its format, quantity, publishing channels, suggested owner, validation queries, and success metric. “Strengthen content” or “improve authority” is not an acceptable standalone recommendation.
