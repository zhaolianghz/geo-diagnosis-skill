import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_report import ReportValidationError, render_report  # noqa: E402


class RenderReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "examples" / "jinge-esports.json").read_text(encoding="utf-8"))

    def test_renders_complete_consulting_report(self):
        html = render_report(self.data)
        required = [
            "执行摘要",
            "核心指标",
            "GEO 能力评分",
            "AI 搜索表现",
            "竞争格局",
            "问题优先级",
            "机会地图",
            "30 / 60 / 90 天路线图",
            "方法与限制",
        ]
        for heading in required:
            self.assertIn(heading, html)
        self.assertIn("77", html)
        self.assertIn("爱电竞", html)
        self.assertIn("OBSERVED", html)
        self.assertIn("INFERRED", html)

    def test_uses_selected_style_without_changing_content(self):
        boardroom = render_report(self.data)
        technology_data = dict(self.data, style="B")
        technology = render_report(technology_data)
        self.assertIn("--accent:#9a7a3a", boardroom)
        self.assertIn("--accent:#315f86", technology)
        self.assertIn(self.data["executive_summary"], boardroom)
        self.assertIn(self.data["executive_summary"], technology)

    def test_escapes_untrusted_text(self):
        data = dict(self.data)
        data["entity"] = '<script>alert("x")</script>'
        html = render_report(data)
        self.assertNotIn('<script>alert("x")</script>', html)
        self.assertIn("&lt;script&gt;", html)

    def test_contains_responsive_and_print_rules(self):
        html = render_report(self.data)
        self.assertIn("@media (max-width: 760px)", html)
        self.assertIn("@media print", html)
        self.assertIn("overflow-x:auto", html)

    def test_rejects_missing_required_sections(self):
        data = dict(self.data)
        del data["roadmap"]
        with self.assertRaises(ReportValidationError):
            render_report(data)

    def test_rejects_invalid_dimension_and_opportunity_values(self):
        bad_dimension = json.loads(json.dumps(self.data))
        bad_dimension["score_dimensions"][0]["score"] = 21
        with self.assertRaises(ReportValidationError):
            render_report(bad_dimension)

        bad_opportunity = json.loads(json.dumps(self.data))
        bad_opportunity["opportunities"][0]["value"] = 6
        with self.assertRaises(ReportValidationError):
            render_report(bad_opportunity)

    def test_rejects_invalid_evidence_state(self):
        data = json.loads(json.dumps(self.data))
        data["issues"][0]["evidence"] = "PROBABLY"
        with self.assertRaises(ReportValidationError):
            render_report(data)

    def test_cli_writes_utf8_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.html"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "render_report.py"),
                    str(ROOT / "examples" / "jinge-esports.json"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("竞鹅电竞", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
