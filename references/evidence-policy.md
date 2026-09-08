# Evidence Policy

Read this reference before converting research or platform results into findings.

## Evidence states

| State | Use when | Minimum record |
|---|---|---|
| `OBSERVED` | The agent directly obtained the page, file, answer, screenshot, or API response during this run | Source/platform, query or URL, date, raw evidence or faithful excerpt |
| `VERIFIED` | A material fact is supported by a reliable public source or independent sources | Source name, URL or file reference, access date |
| `INFERRED` | A conclusion follows from verified facts, proxy signals, content coverage, or known platform tendencies | Inputs used and the reasoning boundary |
| `UNKNOWN` | Evidence is missing, inaccessible, contradictory, or too weak | What is missing and how it could be verified |

Source quality grades and evidence states are different concepts. A government page may be a high-quality source and produce a `VERIFIED` fact; it does not make a future-ranking prediction `VERIFIED`.

## Platform test record

An AI-platform result is `OBSERVED` only when the actual platform response was obtained. Record:

- platform and model when visible;
- date, language, region, login state when relevant;
- exact query;
- whether the entity appeared;
- first position, proactive recommendation, cited sources, competitors, and factual errors;
- raw answer or screenshot reference.

If a platform is inaccessible, mark it `UNKNOWN`. If behavior is estimated from platform characteristics or public content, mark it `INFERRED` and label the section “模拟/推断”，never “实测”.

Question-level KPI calculations may include `OBSERVED`, `VERIFIED`, and clearly labeled `INFERRED` rows, but must exclude `UNKNOWN`. When inferred rows are included, the KPI note and limitations must make that boundary visible. Use only `OBSERVED` rows for a claim named “live test” or “platform benchmark”.

## Conflicts and uncertainty

- Keep conflicting values visible with their respective sources.
- Do not select the most convenient value without an explicit basis.
- Exclude `UNKNOWN` claims from quantitative scoring.
- When proxy data contributes to a score, disclose its weight and confidence.
- Separate current findings from forward-looking hypotheses.

## Language rules

Use “预计、假设、建议复测” for future effects. Do not write “保证进入 Top 3”“30 天必达” or equivalent claims. A roadmap target is an experiment objective, not a commitment.
