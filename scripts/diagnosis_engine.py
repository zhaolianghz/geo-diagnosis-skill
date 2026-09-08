#!/usr/bin/env python3
"""Deterministic calculations for GEO diagnosis reports."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


class DiagnosisValidationError(ValueError):
    pass


QUERY_STATES = {"S0", "S1", "S2", "S3", "S4", "S5"}
EVIDENCE_STATES = {"OBSERVED", "VERIFIED", "INFERRED", "UNKNOWN"}


WEIGHT_PROFILES = {
    "BRAND": {
        "profile": "BRAND_V1",
        "dimensions": [
            {"name": "实体清晰度", "weight": 15},
            {"name": "知识完整度", "weight": 15},
            {"name": "权威与证明", "weight": 15},
            {"name": "第三方信任", "weight": 10},
            {"name": "AI 可见度", "weight": 15},
            {"name": "AI 推荐力", "weight": 15},
            {"name": "竞争占位", "weight": 10},
            {"name": "跨平台一致性", "weight": 5},
        ],
    },
    "LOCAL": {
        "profile": "LOCAL_V1",
        "dimensions": [
            {"name": "实体清晰度", "weight": 10},
            {"name": "知识完整度", "weight": 10},
            {"name": "权威与证明", "weight": 5},
            {"name": "第三方信任", "weight": 20},
            {"name": "AI 可见度", "weight": 15},
            {"name": "AI 推荐力", "weight": 20},
            {"name": "竞争占位", "weight": 10},
            {"name": "跨平台一致性", "weight": 10},
        ],
    },
    "B2B": {
        "profile": "B2B_V1",
        "dimensions": [
            {"name": "实体清晰度", "weight": 10},
            {"name": "知识完整度", "weight": 15},
            {"name": "权威与证明", "weight": 20},
            {"name": "第三方信任", "weight": 10},
            {"name": "AI 可见度", "weight": 10},
            {"name": "AI 推荐力", "weight": 10},
            {"name": "竞争占位", "weight": 10},
            {"name": "跨平台一致性", "weight": 5},
            {"name": "商业证明", "weight": 10},
        ],
    },
    "PRODUCT": {
        "profile": "PRODUCT_V1",
        "dimensions": [
            {"name": "实体清晰度", "weight": 10},
            {"name": "知识完整度", "weight": 20},
            {"name": "权威与证明", "weight": 10},
            {"name": "第三方信任", "weight": 15},
            {"name": "AI 可见度", "weight": 15},
            {"name": "AI 推荐力", "weight": 15},
            {"name": "竞争占位", "weight": 10},
            {"name": "跨平台一致性", "weight": 5},
        ],
    },
    "PERSON": {
        "profile": "PERSON_V1",
        "dimensions": [
            {"name": "实体清晰度", "weight": 15},
            {"name": "知识完整度", "weight": 15},
            {"name": "权威与证明", "weight": 20},
            {"name": "第三方信任", "weight": 15},
            {"name": "AI 可见度", "weight": 15},
            {"name": "AI 推荐力", "weight": 10},
            {"name": "竞争占位", "weight": 5},
            {"name": "跨平台一致性", "weight": 5},
        ],
    },
}

PROFILE_ALIASES = {
    "RESTAURANT": "LOCAL",
}


def get_weight_profile(entity_type: str) -> dict[str, Any]:
    """Return the recommended scoring weights for an entity type."""
    key = PROFILE_ALIASES.get(entity_type.upper(), entity_type.upper())
    if key not in WEIGHT_PROFILES:
        raise DiagnosisValidationError(
            "weight profile must be BRAND, LOCAL, RESTAURANT, B2B, PRODUCT, or PERSON"
        )
    return deepcopy(WEIGHT_PROFILES[key])


def _percent(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 1)


def apply_query_weights(rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    """Attach normalized query weights and disclose how they were obtained."""
    records = deepcopy(list(rows))
    explicit_count = sum("weight" in row for row in records)
    if explicit_count and explicit_count != len(records):
        raise DiagnosisValidationError("query weights must be supplied for every row or omitted for every row")

    if explicit_count:
        bases = [row.get("weight") for row in records]
        if not all(isinstance(value, (int, float)) and value > 0 for value in bases):
            raise DiagnosisValidationError("query weights must be positive numbers")
        if round(sum(bases), 6) != 100:
            raise DiagnosisValidationError("explicit query weights must total 100")
        method = "EXPLICIT"
    else:
        commercial_values = [row.get("business_value") for row in records]
        if records and all(isinstance(value, (int, float)) and 1 <= value <= 5 for value in commercial_values):
            bases = commercial_values
            method = "BUSINESS_VALUE"
        else:
            bases = [1 for _ in records]
            method = "EQUAL"

    total = sum(bases)
    normalized = [round(value / total * 100, 2) for value in bases] if total else []
    if normalized:
        normalized[-1] = round(normalized[-1] + (100 - sum(normalized)), 2)
    for row, weight in zip(records, normalized):
        row["query_weight"] = weight
    return records, method


def compute_query_metrics(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records, weighting_method = apply_query_weights(rows)
    for row in records:
        if row.get("state") not in QUERY_STATES:
            raise DiagnosisValidationError("query state must be S0, S1, S2, S3, S4, or S5")
        if row.get("evidence") not in EVIDENCE_STATES:
            raise DiagnosisValidationError("query evidence must be OBSERVED, VERIFIED, INFERRED, or UNKNOWN")
        checked = row.get("checked_facts", 0)
        accurate = row.get("accurate_facts", 0)
        if not all(isinstance(value, int) and value >= 0 for value in (checked, accurate)) or accurate > checked:
            raise DiagnosisValidationError("accurate_facts must be between 0 and checked_facts")

    effective = [row for row in records if row["evidence"] != "UNKNOWN"]
    visible = [row for row in effective if row["state"] in {"S3", "S4", "S5"}]
    recommended = [row for row in effective if row["state"] in {"S4", "S5"}]
    top3 = [row for row in effective if isinstance(row.get("rank"), int) and row["rank"] <= 3]
    competitor_losses = [row for row in effective if row["state"] == "S2"]
    cited_recommendations = [row for row in recommended if row.get("has_citation") is True]
    effective_weight = sum(row["query_weight"] for row in effective)
    visible_weight = sum(row["query_weight"] for row in visible)
    recommended_weight = sum(row["query_weight"] for row in recommended)
    top3_weight = sum(row["query_weight"] for row in top3)
    competitor_loss_weight = sum(row["query_weight"] for row in competitor_losses)
    cited_weight = sum(row["query_weight"] for row in cited_recommendations)
    checked_facts = sum(row.get("checked_facts", 0) for row in effective)
    accurate_facts = sum(row.get("accurate_facts", 0) for row in effective)

    return {
        "total_queries": len(records),
        "effective_queries": len(effective),
        "unknown_queries": len(records) - len(effective),
        "query_weighting": weighting_method,
        "visibility_rate": _percent(visible_weight, effective_weight),
        "recommendation_rate": _percent(recommended_weight, effective_weight),
        "top3_rate": _percent(top3_weight, effective_weight),
        "competitor_loss_rate": _percent(competitor_loss_weight, effective_weight),
        "citation_coverage": _percent(cited_weight, recommended_weight),
        "entity_accuracy": _percent(accurate_facts, checked_facts),
    }


def compute_weighted_score(model: dict[str, Any]) -> dict[str, Any]:
    dimensions = deepcopy(model.get("dimensions", []))
    if not dimensions:
        raise DiagnosisValidationError("scoring model requires at least one dimension")
    total_weight = sum(item.get("weight", 0) for item in dimensions)
    if round(total_weight, 6) != 100:
        raise DiagnosisValidationError("scoring weights must total 100")
    for item in dimensions:
        raw_score = item.get("raw_score")
        weight = item.get("weight")
        if not isinstance(raw_score, (int, float)) or not 0 <= raw_score <= 100:
            raise DiagnosisValidationError("dimension raw_score must be from 0 to 100")
        if not isinstance(weight, (int, float)) or weight <= 0:
            raise DiagnosisValidationError("dimension weight must be positive")
        item["contribution"] = round(raw_score * weight / 100, 2)
    score = round(sum(item["contribution"] for item in dimensions), 1)
    return {"profile": model.get("profile", "CUSTOM"), "score": score, "dimensions": dimensions}


def compute_opportunity_score(item: dict[str, Any]) -> int:
    weights = {
        "business_value": 0.35,
        "gap": 0.30,
        "feasibility": 0.20,
        "evidence_confidence": 0.15,
    }
    for key in weights:
        value = item.get(key)
        if not isinstance(value, int) or not 1 <= value <= 5:
            raise DiagnosisValidationError(f"{key} must be an integer from 1 to 5")
    normalized = sum(item[key] / 5 * weight for key, weight in weights.items())
    return round(normalized * 100)


def enrich_report(data: dict[str, Any]) -> dict[str, Any]:
    enriched = deepcopy(data)
    if "query_universe" not in enriched:
        raise DiagnosisValidationError("query_universe is required")
    if "scoring_model" not in enriched:
        raise DiagnosisValidationError("scoring_model is required")
    enriched["query_universe"], _ = apply_query_weights(enriched["query_universe"])
    enriched["computed_metrics"] = compute_query_metrics(enriched["query_universe"])
    scoring = compute_weighted_score(enriched["scoring_model"])
    enriched["scoring_model"] = scoring
    enriched["score"] = scoring["score"]
    enriched["opportunities"] = [
        dict(item, opportunity_score=compute_opportunity_score(item))
        for item in enriched.get("opportunities", [])
    ]
    return enriched
