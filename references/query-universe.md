# GEO Query Universe

Read this reference whenever the report must explain “currently monitored GEO keywords/questions, their weights, and what should be added.”

## Use questions, not a keyword dump

Generative search is conversational. The inventory must therefore record the exact user question that will be tested, while `cluster` acts as the keyword/topic grouping.

A full diagnosis uses 20–50 stable questions. Use 8–12 only for an explicitly requested quick scan. Keep the final baseline unchanged during later retests unless a business change justifies a versioned update.

## Required coverage

Build the inventory from all commercially relevant clusters:

1. Entity recognition — “X 是什么？” “X 与旧名称是否为同一实体？”
2. Category recommendation — “有哪些值得推荐的 Y？”
3. Geography — “城市 / 商圈 + Y 推荐”
4. Audience — “适合某类人群的 Y”
5. Scenario — “某场景应该选择什么？”
6. Comparison — “X 和竞品有什么区别？”
7. Commercial decision — price, ROI, cases, suppliers, franchise, procurement.
8. Trust and risk — reviews, complaints, qualifications, accuracy, safety.

Add secondary clusters based on entity type:

- `LOCAL` / `RESTAURANT`: POI, distance, opening hours, menu/service, reviews, neighborhood, occasion.
- `B2B`: problem, solution, industry, buyer role, implementation, integration, case, ROI, procurement risk.
- `PRODUCT`: feature, specification, compatibility, comparison, use case, price, review, after-sales.
- `PERSON`: identity, expertise, works, credentials, viewpoint, speaking/consulting intent, reputation.

## Required row fields

Every question records:

- exact query text;
- cluster and intent;
- business goal and user decision stage;
- current state `S0`–`S5`;
- rank when observable;
- evidence state;
- citation presence and checked facts;
- business value and competition, each 1–5;
- suggested asset and concise finding.

Do not invent search volume. If reliable search-volume data is unavailable, use business value, observed platform outcomes, and evidence confidence instead.

## Query weighting

Prefer explicit weights when the client has a known revenue funnel, lead value, store priority, or strategic market allocation. Supply a positive `weight` for every query and make the total 100.

When explicit weights are unavailable, the engine uses:

```text
query weight = question business value / total business value of all questions × 100
```

If business value is also unavailable, the engine uses equal weights. The report discloses which method was applied.

Business-value rubric:

| Score | Meaning |
|---:|---|
| 5 | Directly affects purchase, lead, visit, franchise, procurement, or reputation risk |
| 4 | Strong consideration-stage or differentiated scenario |
| 3 | Useful discovery demand with indirect commercial value |
| 2 | Peripheral awareness or weak-fit demand |
| 1 | Low relevance; retain only when needed for entity disambiguation or monitoring |

Competition rubric:

| Score | Meaning |
|---:|---|
| 5 | Several direct competitors consistently occupy the recommendation set |
| 4 | One or more strong competitors with good supporting evidence |
| 3 | Mixed or unstable competitive presence |
| 2 | Limited competing content or weak recommendations |
| 1 | Little observed competition; evidence should still be recorded |

## Minimum output standard

The final HTML must show the complete inventory, not only a management sample. At minimum display: query, cluster, intent, goal, stage, state, rank, question weight, business value, competition, evidence state, and suggested asset.

The condensed AI-search table can highlight representative questions, but it cannot replace the full query universe.
