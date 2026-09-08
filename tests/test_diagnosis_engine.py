import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from diagnosis_engine import (  # noqa: E402
    DiagnosisValidationError,
    compute_opportunity_score,
    compute_query_metrics,
    compute_weighted_score,
    enrich_report,
    get_weight_profile,
)


class QueryMetricTests(unittest.TestCase):
    def test_uses_query_weights_for_business_relevant_metrics(self):
        rows = [
            {"state": "S5", "rank": 1, "has_citation": True, "checked_facts": 0, "accurate_facts": 0, "evidence": "OBSERVED", "weight": 70},
            {"state": "S2", "rank": None, "has_citation": False, "checked_facts": 0, "accurate_facts": 0, "evidence": "OBSERVED", "weight": 30},
        ]
        metrics = compute_query_metrics(rows)
        self.assertEqual(metrics["visibility_rate"], 70.0)
        self.assertEqual(metrics["recommendation_rate"], 70.0)
        self.assertEqual(metrics["top3_rate"], 70.0)
        self.assertEqual(metrics["competitor_loss_rate"], 30.0)
        self.assertEqual(metrics["query_weighting"], "EXPLICIT")

    def test_rejects_partial_or_invalid_explicit_query_weights(self):
        with self.assertRaises(DiagnosisValidationError):
            compute_query_metrics([
                {"state": "S5", "evidence": "OBSERVED", "weight": 60},
                {"state": "S1", "evidence": "OBSERVED"},
            ])

    def test_computes_metrics_from_row_level_results(self):
        rows = [
            {"state": "S5", "rank": 1, "has_citation": True, "checked_facts": 4, "accurate_facts": 4, "evidence": "OBSERVED"},
            {"state": "S4", "rank": 3, "has_citation": False, "checked_facts": 3, "accurate_facts": 2, "evidence": "OBSERVED"},
            {"state": "S3", "rank": 6, "has_citation": False, "checked_facts": 2, "accurate_facts": 2, "evidence": "VERIFIED"},
            {"state": "S2", "rank": None, "has_citation": False, "checked_facts": 0, "accurate_facts": 0, "evidence": "INFERRED"},
            {"state": "S1", "rank": None, "has_citation": False, "checked_facts": 0, "accurate_facts": 0, "evidence": "UNKNOWN"}
        ]
        metrics = compute_query_metrics(rows)
        self.assertEqual(metrics["effective_queries"], 4)
        self.assertEqual(metrics["visibility_rate"], 75.0)
        self.assertEqual(metrics["recommendation_rate"], 50.0)
        self.assertEqual(metrics["top3_rate"], 50.0)
        self.assertEqual(metrics["competitor_loss_rate"], 25.0)
        self.assertEqual(metrics["citation_coverage"], 50.0)
        self.assertEqual(metrics["entity_accuracy"], 88.9)

    def test_rejects_unknown_query_state(self):
        with self.assertRaises(DiagnosisValidationError):
            compute_query_metrics([{"state": "MAYBE", "evidence": "OBSERVED"}])


class ScoringTests(unittest.TestCase):
    def test_provides_entity_specific_weight_profiles(self):
        brand = get_weight_profile("BRAND")
        local = get_weight_profile("RESTAURANT")
        b2b = get_weight_profile("B2B")

        self.assertEqual(sum(item["weight"] for item in brand["dimensions"]), 100)
        self.assertEqual(local["profile"], "LOCAL_V1")
        self.assertGreater(
            next(item["weight"] for item in b2b["dimensions"] if item["name"] == "权威与证明"),
            next(item["weight"] for item in brand["dimensions"] if item["name"] == "权威与证明"),
        )

    def test_rejects_unknown_weight_profile(self):
        with self.assertRaises(DiagnosisValidationError):
            get_weight_profile("UNKNOWN")

    def test_computes_transparent_weighted_score(self):
        model = {
            "profile": "TEST",
            "dimensions": [
                {"name": "Entity", "raw_score": 80, "weight": 40, "rationale": "verified facts"},
                {"name": "Recommendation", "raw_score": 70, "weight": 60, "rationale": "query tests"}
            ]
        }
        result = compute_weighted_score(model)
        self.assertEqual(result["score"], 74.0)
        self.assertEqual(result["dimensions"][0]["contribution"], 32.0)
        self.assertEqual(result["dimensions"][1]["contribution"], 42.0)

    def test_rejects_weights_that_do_not_total_100(self):
        model = {"profile": "BAD", "dimensions": [{"name": "Only", "raw_score": 80, "weight": 80}]}
        with self.assertRaises(DiagnosisValidationError):
            compute_weighted_score(model)


class OpportunityTests(unittest.TestCase):
    def test_computes_weighted_opportunity_score(self):
        item = {"business_value": 5, "gap": 4, "feasibility": 3, "evidence_confidence": 4}
        self.assertEqual(compute_opportunity_score(item), 83)

    def test_rejects_out_of_range_opportunity_inputs(self):
        with self.assertRaises(DiagnosisValidationError):
            compute_opportunity_score({"business_value": 6, "gap": 4, "feasibility": 3, "evidence_confidence": 4})


class EnrichmentTests(unittest.TestCase):
    def test_enriches_report_without_trusting_manual_kpis(self):
        data = {
            "query_universe": [
                {"state": "S5", "rank": 1, "has_citation": True, "checked_facts": 1, "accurate_facts": 1, "evidence": "OBSERVED"}
            ],
            "scoring_model": {
                "profile": "TEST",
                "dimensions": [{"name": "All", "raw_score": 77, "weight": 100, "rationale": "fixture"}]
            },
            "opportunities": [
                {"business_value": 5, "gap": 4, "feasibility": 3, "evidence_confidence": 4}
            ]
        }
        enriched = enrich_report(data)
        self.assertEqual(enriched["score"], 77.0)
        self.assertEqual(enriched["computed_metrics"]["visibility_rate"], 100.0)
        self.assertEqual(enriched["opportunities"][0]["opportunity_score"], 83)


if __name__ == "__main__":
    unittest.main()
