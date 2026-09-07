#!/usr/bin/env python3
"""Render a self-contained GEO diagnosis HTML report from JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable


class ReportValidationError(ValueError):
    pass


REQUIRED = (
    "report_title",
    "entity",
    "date",
    "style",
    "score",
    "grade",
    "executive_summary",
    "kpis",
    "score_dimensions",
    "search_performance",
    "competitors",
    "issues",
    "opportunities",
    "roadmap",
    "evidence_summary",
    "limitations",
)

THEMES = {
    "A": {"paper": "#f4f1ea", "sheet": "#fbfaf6", "ink": "#171715", "muted": "#6e6a61", "line": "#d8d2c7", "accent": "#9a7a3a", "soft": "#ebe3d2"},
    "B": {"paper": "#eef1f3", "sheet": "#fbfcfd", "ink": "#14202a", "muted": "#66717a", "line": "#d5dde2", "accent": "#315f86", "soft": "#e1eaf0"},
    "C": {"paper": "#f3eee9", "sheet": "#fdfaf7", "ink": "#241d1a", "muted": "#746860", "line": "#ded3ca", "accent": "#8b5746", "soft": "#eee1da"},
    "D": {"paper": "#eceeed", "sheet": "#ffffff", "ink": "#16201b", "muted": "#657068", "line": "#d3d9d5", "accent": "#476b58", "soft": "#e3ebe6"},
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def validate(data: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise ReportValidationError("Missing required fields: " + ", ".join(missing))
    if data["style"] not in THEMES:
        raise ReportValidationError("style must be one of A, B, C, D")
    if not isinstance(data["score"], (int, float)) or not 0 <= data["score"] <= 100:
        raise ReportValidationError("score must be a number from 0 to 100")
    for key in ("kpis", "score_dimensions", "competitors", "issues", "opportunities", "roadmap"):
        if not isinstance(data[key], list) or not data[key]:
            raise ReportValidationError(f"{key} must be a non-empty list")
    for item in data["score_dimensions"]:
        score, maximum = item.get("score"), item.get("max")
        if not all(isinstance(value, (int, float)) for value in (score, maximum)) or maximum <= 0 or not 0 <= score <= maximum:
            raise ReportValidationError("each score dimension must satisfy 0 <= score <= max")
    for item in data["opportunities"]:
        axes = (item.get("value"), item.get("gap"), item.get("feasibility"))
        if not all(isinstance(value, int) and 1 <= value <= 5 for value in axes):
            raise ReportValidationError("opportunity value, gap, and feasibility must be integers from 1 to 5")
    evidence_states = {"OBSERVED", "VERIFIED", "INFERRED", "UNKNOWN"}
    reported_states = [item.get("evidence") for item in data["issues"]]
    reported_states += [item.get("state") for item in data["evidence_summary"]]
    reported_states.append(data["search_performance"].get("evidence_state"))
    if any(state not in evidence_states for state in reported_states):
        raise ReportValidationError("evidence states must be OBSERVED, VERIFIED, INFERRED, or UNKNOWN")


def join_items(items: Iterable[str]) -> str:
    return "".join(items)


def evidence_badge(state: str) -> str:
    normalized = state.upper()
    return f'<span class="evidence-badge {esc(normalized.lower())}">{esc(normalized)}</span>'


def section_head(number: str, title: str) -> str:
    return f'<header class="section-head"><div class="section-no">Section {esc(number)}</div><h2>{esc(title)}</h2></header>'


def render_report(data: dict[str, Any]) -> str:
    validate(data)
    theme = THEMES[data["style"]]
    css_path = Path(__file__).resolve().parents[1] / "assets" / "report.css"
    css = css_path.read_text(encoding="utf-8")
    overrides = ":root{" + "".join(f"--{key}:{value};" for key, value in theme.items()) + "}"
    aliases = " / ".join(esc(x) for x in data.get("entity_aliases", []))

    kpis = join_items(
        f'<div class="kpi"><div class="kpi-label">{esc(item["label"])}</div><div class="kpi-value">{esc(item["value"])}</div><div class="kpi-note">{esc(item.get("note", ""))}</div></div>'
        for item in data["kpis"]
    )
    dimensions = join_items(
        f'<div class="dimension"><div class="dimension-name">{esc(item["name"])}</div><div class="bar"><i style="width:{item["score"] / item["max"] * 100:.1f}%"></i></div><div class="dimension-score">{esc(item["score"])} / {esc(item["max"])}</div><small>{esc(item.get("evidence", ""))}</small></div>'
        for item in data["score_dimensions"]
    )
    search_rows = join_items(
        "<tr>"
        f'<td>{esc(row["query"])}</td><td>{esc(row["category"])}</td>'
        f'<td><span class="status {esc(row["status"].lower().replace(" ", "-"))}">{esc(row["status"])}</span></td>'
        f'<td>{esc(row["rank"])}</td><td>{esc(row["coverage"])}</td><td>{esc(row["finding"])}</td>'
        "</tr>"
        for row in data["search_performance"]["rows"]
    )
    competitors = join_items(
        f'<div class="competitor {"is-subject" if row["name"] in (data["entity"], "竞鹅电竞") else ""}"><div>{esc(row["name"])}</div><div class="bar"><i style="width:{esc(row["score"])}%"></i></div><strong>{esc(row["score"])}</strong><div class="position">{esc(row["position"])}</div></div>'
        for row in data["competitors"]
    )
    issues = join_items(
        f'<article class="issue"><div class="priority">{esc(row["priority"])}</div><div><strong>{esc(row["title"])}</strong></div><div><span class="kicker">影响</span><p>{esc(row["impact"])}</p></div><div><span class="kicker">行动</span><p>{esc(row["action"])}</p></div><div>{evidence_badge(row["evidence"])}</div></article>'
        for row in data["issues"]
    )
    opportunities = join_items(
        f'<div class="opportunity" style="left:{10 + (row["value"] - 1) * 20}%;bottom:{10 + (row["feasibility"] - 1) * 20}%">{esc(row["name"])}<em>{esc(row["priority"])} · 缺口 {esc(row["gap"])}/5</em></div>'
        for row in data["opportunities"]
    )
    roadmap = join_items(
        f'<div class="phase"><div class="phase-time">{esc(row["window"])}</div><div class="phase-body"><div class="theme">{esc(row["theme"])}</div><h3>{esc(row["target"])}</h3><ul>{join_items(f"<li>{esc(action)}</li>" for action in row["actions"])}</ul></div></div>'
        for row in data["roadmap"]
    )
    evidence = join_items(
        f'<div class="evidence-item">{evidence_badge(row["state"])}<p>{esc(row["definition"])}</p><p><strong>本报告：</strong>{esc(row.get("count", ""))}</p></div>'
        for row in data["evidence_summary"]
    )
    limitations = join_items(f"<li>{esc(item)}</li>" for item in data["limitations"])
    circumference = 2 * 3.14159 * 88
    dash = circumference * float(data["score"]) / 100

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<link rel="icon" href="data:,">
<title>{esc(data["report_title"])}</title>
<style>{css}\n{overrides}</style>
</head>
<body>
<main class="report">
  <section class="cover">
    <div class="cover-top">
      <div class="kicker">Generative Engine Optimization · Diagnostic Report</div>
      <div class="cover-rule"></div>
      <h1>{esc(data["report_title"])}</h1>
      <p class="cover-subtitle">面向生成式搜索时代的品牌可见度、推荐能力与增长机会评估</p>
    </div>
    <div class="cover-bottom">
      <div class="cover-meta">
        <div><span>诊断对象</span><strong>{esc(data["entity"])}</strong></div>
        <div><span>对象类型</span><strong>{esc(data.get("entity_type", "—"))}</strong></div>
        <div><span>诊断范围</span><strong>{esc(data.get("scope", "—"))}</strong></div>
        <div><span>报告日期</span><strong>{esc(data["date"])}</strong></div>
      </div>
    </div>
  </section>
  <div class="content">
    <nav class="toc"><div class="section-no">Contents</div><ol><li>执行摘要</li><li>核心指标</li><li>GEO 能力评分</li><li>AI 搜索表现</li><li>竞争格局</li><li>问题优先级</li><li>机会地图</li><li>30 / 60 / 90 天路线图</li><li>方法与限制</li></ol></nav>

    <section class="section">{section_head("01", "执行摘要")}<p class="lede">{esc(data["executive_summary"])}</p><div class="summary-grid"><div><h3>诊断对象</h3><p>{esc(data["entity"])}{f"（{aliases}）" if aliases else ""}</p><p>{esc(data.get("industry", ""))}</p></div><div class="decision-note"><strong>管理层判断</strong><p>品牌基础认知已经形成，下一阶段的重点不是扩大泛曝光，而是修复实体歧义、补足高价值场景，并将腾讯 IP 优势转化为稳定推荐理由。</p></div></div></section>

    <section class="section">{section_head("02", "核心指标")}<div class="kpis">{kpis}</div></section>

    <section class="section">{section_head("03", "GEO 能力评分")}<div class="score-hero"><div class="score-ring"><svg viewBox="0 0 200 200" aria-label="GEO score {esc(data["score"])}"><circle class="track" cx="100" cy="100" r="88"/><circle class="value" cx="100" cy="100" r="88" stroke-dasharray="{dash:.2f} {circumference:.2f}"/></svg><div class="score-copy"><strong>{esc(data["score"])}</strong><span>out of 100</span></div></div><div class="score-context"><h3>{esc(data["grade"])}</h3><p>{esc(data.get("benchmark", ""))}</p><p>强项集中在品牌实体、内容覆盖与第三方信任；主要短板是推荐位稳定性和行业权威资产。</p></div></div><div class="dimension-list">{dimensions}</div></section>

    <section class="section">{section_head("04", "AI 搜索表现")}<div class="method-note"><strong>{evidence_badge(data["search_performance"]["evidence_state"])}</strong><div>{esc(data["search_performance"]["disclaimer"])}</div></div><div class="table-wrap"><table><thead><tr><th>核心问题</th><th>类型</th><th>状态</th><th>排名</th><th>覆盖</th><th>主要发现</th></tr></thead><tbody>{search_rows}</tbody></table></div></section>

    <section class="section">{section_head("05", "竞争格局")}<p class="lede">竞鹅位于头部阵营，但与爱电竞、网鱼仍有 <strong>7–8 分</strong>差距；差距主要来自推荐概率、内容密度和权威资产，而不是品牌独特性。</p><div class="competitor-chart">{competitors}</div></section>

    <section class="section">{section_head("06", "问题优先级")}<p>优先级同时考虑商业影响、修复时效与证据确定性。P0 应在一周内启动，P1 纳入首月增长计划。</p>{issues}</section>

    <section class="section">{section_head("07", "机会地图")}<p>横轴表示商业价值，纵轴表示可实现性。右上区域应优先配置内容与渠道资源；标签同时显示当前缺口。</p><div class="opp-map">{opportunities}</div></section>

    <section class="section">{section_head("08", "30 / 60 / 90 天路线图")}<div class="roadmap">{roadmap}</div></section>

    <section class="section">{section_head("09", "方法与限制")}<div class="evidence-grid">{evidence}</div><ul class="limitations">{limitations}</ul></section>
  </div>
  <footer class="footer"><span>{esc(data["report_title"])} · {esc(data["version"])}</span><span>仅基于所列证据，不构成投资建议或商业承诺</span></footer>
</main>
</body>
</html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_html", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input_json.read_text(encoding="utf-8"))
        output = render_report(data)
        args.output_html.parent.mkdir(parents=True, exist_ok=True)
        args.output_html.write_text(output, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ReportValidationError) as exc:
        parser.error(str(exc))
    print(f"Rendered {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
