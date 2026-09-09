#!/usr/bin/env python3
"""Render a self-contained GEO diagnosis HTML report from JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from diagnosis_engine import DiagnosisValidationError, enrich_report


class ReportValidationError(ValueError):
    pass


REQUIRED = (
    "report_title",
    "entity",
    "date",
    "style",
    "grade",
    "executive_summary",
    "scoring_model",
    "query_universe",
    "search_performance",
    "competitors",
    "issues",
    "asset_blueprint",
    "opportunities",
    "roadmap",
    "evidence_summary",
    "evidence_registry",
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
    for key in ("query_universe", "competitors", "issues", "asset_blueprint", "opportunities", "roadmap", "evidence_registry"):
        if not isinstance(data[key], list) or not data[key]:
            raise ReportValidationError(f"{key} must be a non-empty list")
    for item in data["opportunities"]:
        axes = (item.get("business_value"), item.get("gap"), item.get("feasibility"), item.get("evidence_confidence"))
        if not all(isinstance(value, int) and 1 <= value <= 5 for value in axes):
            raise ReportValidationError("opportunity inputs must be integers from 1 to 5")
        legacy_value = item.get("value")
        if legacy_value is not None and (not isinstance(legacy_value, int) or not 1 <= legacy_value <= 5):
            raise ReportValidationError("legacy opportunity value must be an integer from 1 to 5")
    query_fields = {
        "query", "cluster", "intent", "goal", "stage", "state", "business_value",
        "competition", "evidence", "suggested_asset",
    }
    for item in data["query_universe"]:
        missing_query_fields = sorted(query_fields - item.keys())
        if missing_query_fields:
            raise ReportValidationError("query row missing fields: " + ", ".join(missing_query_fields))
    asset_fields = {"priority", "problem", "asset", "format", "quantity", "channels", "owner", "validation_queries", "metric"}
    for item in data["asset_blueprint"]:
        missing_asset_fields = sorted(asset_fields - item.keys())
        if missing_asset_fields:
            raise ReportValidationError("asset row missing fields: " + ", ".join(missing_asset_fields))
    evidence_states = {"OBSERVED", "VERIFIED", "INFERRED", "UNKNOWN"}
    reported_states = [item.get("evidence") for item in data["issues"]]
    reported_states += [item.get("evidence") for item in data["query_universe"]]
    reported_states += [item.get("state") for item in data["evidence_summary"]]
    reported_states += [item.get("state") for item in data["evidence_registry"]]
    reported_states.append(data["search_performance"].get("evidence_state"))
    if any(state not in evidence_states for state in reported_states):
        raise ReportValidationError("evidence states must be OBSERVED, VERIFIED, INFERRED, or UNKNOWN")


def join_items(items: Iterable[str]) -> str:
    return "".join(items)


def evidence_badge(state: str) -> str:
    normalized = state.upper()
    return f'<span class="evidence-badge {esc(normalized.lower())}">{esc(normalized)}</span>'


def source_link(url: Any) -> str:
    value = str(url or "").strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return f'<br><a class="source-link" href="{esc(value)}" target="_blank" rel="noopener noreferrer">打开来源 ↗</a>'


def section_head(number: str, title: str) -> str:
    return f'<header class="section-head"><div class="section-no">Section {esc(number)}</div><h2>{esc(title)}</h2></header>'


def metric_value(value: Any) -> str:
    return "—" if value is None else f"{float(value):.1f}%"


def render_report(data: dict[str, Any]) -> str:
    try:
        data = enrich_report(data)
    except DiagnosisValidationError as exc:
        raise ReportValidationError(str(exc)) from exc
    validate(data)
    theme = THEMES[data["style"]]
    css_path = Path(__file__).resolve().parents[1] / "assets" / "report.css"
    css = css_path.read_text(encoding="utf-8")
    overrides = ":root{" + "".join(f"--{key}:{value};" for key, value in theme.items()) + "}"
    aliases = " / ".join(esc(x) for x in data.get("entity_aliases", []))
    subject_names = {data["entity"], *data.get("entity_aliases", [])}

    metrics = data["computed_metrics"]
    weighting_names = {
        "EXPLICIT": "显式业务权重",
        "BUSINESS_VALUE": "商业价值归一化权重",
        "EQUAL": "等权重",
    }
    weighting_label = weighting_names.get(metrics["query_weighting"], metrics["query_weighting"])
    computed_kpis = [
        {"label": "综合评分", "value": f'{data["score"]:.1f}', "note": "由公开权重自动计算"},
        {"label": "AI 可见率", "value": metric_value(metrics["visibility_rate"]), "note": f'{metrics["effective_queries"]} 个有效问题'},
        {"label": "AI 推荐率", "value": metric_value(metrics["recommendation_rate"]), "note": "S4 + S5 / 有效问题"},
        {"label": "Top 3 率", "value": metric_value(metrics["top3_rate"]), "note": "逐条排名自动统计"},
        {"label": "竞品失守率", "value": metric_value(metrics["competitor_loss_rate"]), "note": "S2 / 有效问题"},
        {"label": "引用覆盖率", "value": metric_value(metrics["citation_coverage"]), "note": "有引用的推荐结果"},
        {"label": "事实准确率", "value": metric_value(metrics["entity_accuracy"]), "note": "已核验事实口径"},
    ]
    kpis = join_items(
        f'<div class="kpi"><div class="kpi-label">{esc(item["label"])}</div><div class="kpi-value">{esc(item["value"])}</div><div class="kpi-note">{esc(item["note"])}</div></div>'
        for item in computed_kpis
    )
    score_rows = join_items(
        "<tr>"
        f'<td>{esc(item["name"])}</td><td>{esc(round(item["raw_score"], 1))}%</td>'
        f'<td>{esc(item["weight"])}%</td><td><strong>{esc(item["contribution"])}</strong></td><td>{esc(item.get("rationale", ""))}</td>'
        "</tr>"
        for item in data["scoring_model"]["dimensions"]
    )
    state_names = {"S0": "Unresolved", "S1": "Not Found", "S2": "Competitor Won", "S3": "Mentioned", "S4": "Recommended", "S5": "Preferred"}
    query_rows = join_items(
        "<tr>"
        f'<td class="query-cell">{esc(row["query"])}</td><td>{esc(row["cluster"])}</td><td>{esc(row["intent"])}</td>'
        f'<td>{esc(row["goal"])}</td><td>{esc(row["stage"])}</td><td><span class="status {esc(state_names[row["state"]].lower().replace(" ", "-"))}">{esc(row["state"])} · {esc(state_names[row["state"]])}</span></td>'
        f'<td>{esc(row.get("rank_label", row.get("rank") or "—"))}</td><td><strong>{esc(row["query_weight"])}%</strong></td><td>{esc(row["business_value"])}/5</td><td>{esc(row["competition"])}/5</td>'
        f'<td>{evidence_badge(row["evidence"])}</td><td>{esc(row["suggested_asset"])}</td>'
        "</tr>"
        for row in data["query_universe"]
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
        f'<div class="competitor {"is-subject" if row["name"] in subject_names else ""}"><div>{esc(row["name"])}</div><div class="bar"><i style="width:{esc(row["score"])}%"></i></div><strong>{esc(row["score"])}</strong><div class="position">{esc(row["position"])}</div></div>'
        for row in data["competitors"]
    )
    issues = join_items(
        f'<article class="issue"><div class="priority">{esc(row["priority"])}</div><div><strong>{esc(row["title"])}</strong></div><div><span class="kicker">影响</span><p>{esc(row["impact"])}</p></div><div><span class="kicker">行动</span><p>{esc(row["action"])}</p></div><div>{evidence_badge(row["evidence"])}</div></article>'
        for row in data["issues"]
    )
    opportunities = join_items(
        f'<div class="opportunity" style="left:{10 + (row["business_value"] - 1) * 20}%;bottom:{10 + (row["feasibility"] - 1) * 20}%">{esc(row["name"])}<em>{esc(row["priority"])} · 机会分 {esc(row["opportunity_score"])} · 缺口 {esc(row["gap"])}/5 · 商业价值 {esc(row["business_value"])}/5 · 可实现性 {esc(row["feasibility"])}/5</em></div>'
        for row in data["opportunities"]
    )
    asset_rows = join_items(
        "<tr>"
        f'<td><span class="priority-inline">{esc(row["priority"])}</span></td><td>{esc(row["problem"])}</td><td><strong>{esc(row["asset"])}</strong><br><small>{esc(row["format"])}</small></td>'
        f'<td>{esc(row["quantity"])}</td><td>{esc(" / ".join(row["channels"]))}</td><td>{esc(row["owner"])}</td>'
        f'<td>{esc("；".join(row["validation_queries"]))}</td><td>{esc(row["metric"])}</td>'
        "</tr>"
        for row in data["asset_blueprint"]
    )
    roadmap = join_items(
        f'<div class="phase"><div class="phase-time">{esc(row["window"])}</div><div class="phase-body"><div class="theme">{esc(row["theme"])}</div><h3>{esc(row["target"])}</h3><ul>{join_items(f"<li>{esc(action)}</li>" for action in row["actions"])}</ul></div></div>'
        for row in data["roadmap"]
    )
    evidence = join_items(
        f'<div class="evidence-item">{evidence_badge(row["state"])}<p>{esc(row["definition"])}</p><p><strong>本报告：</strong>{esc(row.get("count", ""))}</p></div>'
        for row in data["evidence_summary"]
    )
    evidence_registry_rows = join_items(
        "<tr>"
        f'<td>{esc(row["id"])}</td><td>{esc(row["claim"])}</td><td>{evidence_badge(row["state"])}</td><td>{esc(row["source"])}{source_link(row.get("url"))}</td>'
        f'<td>{esc(row["source_grade"])}</td><td>{esc(row["date"])}</td><td>{esc(row["supports"])}</td>'
        "</tr>"
        for row in data["evidence_registry"]
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
    <nav class="toc"><div class="section-no">Contents</div><ol><li>执行摘要</li><li>核心指标</li><li>GEO 能力评分</li><li>GEO 搜索问题版图</li><li>AI 搜索表现</li><li>竞争格局</li><li>问题优先级</li><li>机会地图</li><li>内容与知识资产蓝图</li><li>30 / 60 / 90 天路线图</li><li>证据目录</li><li>方法与限制</li></ol></nav>

    <section class="section">{section_head("01", "执行摘要")}<p class="lede">{esc(data["executive_summary"])}</p><div class="summary-grid"><div><h3>诊断对象</h3><p>{esc(data["entity"])}{f"（{aliases}）" if aliases else ""}</p><p>{esc(data.get("industry", ""))}</p></div><div class="decision-note"><strong>管理层判断</strong><p>{esc(data.get("management_judgment", data["executive_summary"]))}</p></div></div></section>

    <section class="section">{section_head("02", "核心指标")}<div class="kpis">{kpis}</div></section>

    <section class="section score-section">{section_head("03", "GEO 能力评分")}<div class="score-hero"><div class="score-ring"><svg viewBox="0 0 200 200" aria-label="GEO score {esc(data["score"])}"><circle class="track" cx="100" cy="100" r="88"/><circle class="value" cx="100" cy="100" r="88" stroke-dasharray="{dash:.2f} {circumference:.2f}"/></svg><div class="score-copy"><strong>{esc(data["score"])}</strong><span>out of 100</span></div></div><div class="score-context"><h3>{esc(data["grade"])}</h3><p>{esc(data.get("benchmark", ""))}</p><p>{esc(data["scoring_model"].get("basis", "总分由维度原始分与公开权重自动计算。"))}</p></div></div><h3 class="subsection-title">权重与得分解释</h3><div class="table-wrap"><table><thead><tr><th>评分维度</th><th>原始得分</th><th>权重</th><th>加权贡献</th><th>评分依据</th></tr></thead><tbody>{score_rows}</tbody></table></div></section>

    <section class="section">{section_head("04", "GEO 搜索问题版图")}<p class="lede">当前诊断覆盖 <strong>{esc(metrics["total_queries"])} 个用户问题</strong>，按问题簇、搜索意图、商业目标和用户决策阶段管理，而不是只罗列孤立关键词。</p><div class="method-note"><strong>Reading guide</strong><div>问题权重决定各问题对 AI 可见率等指标的贡献；本次采用“{esc(weighting_label)}”口径。商业价值与竞争强度均为 1–5 分，状态使用 S0–S5，建议资产直接对应问题缺口。</div></div><div class="table-wrap query-table"><table><thead><tr><th>当前 GEO 搜索问题</th><th>问题簇</th><th>搜索意图</th><th>商业目标</th><th>用户决策阶段</th><th>当前状态</th><th>排名</th><th>问题权重</th><th>商业价值</th><th>竞争强度</th><th>证据</th><th>建议资产</th></tr></thead><tbody>{query_rows}</tbody></table></div></section>

    <section class="section">{section_head("05", "AI 搜索表现")}<div class="method-note"><strong>{evidence_badge(data["search_performance"]["evidence_state"])}</strong><div>{esc(data["search_performance"]["disclaimer"])}</div></div><div class="table-wrap"><table><thead><tr><th>核心问题</th><th>类型</th><th>状态</th><th>排名</th><th>覆盖</th><th>主要发现</th></tr></thead><tbody>{search_rows}</tbody></table></div></section>

    <section class="section">{section_head("06", "竞争格局")}<p class="lede">{esc(data.get("competitive_summary", "对比直接竞品的综合表现、推荐占位和证据资产，识别最值得优先修复的竞争差距。"))}</p><div class="competitor-chart">{competitors}</div></section>

    <section class="section">{section_head("07", "问题优先级")}<p>优先级同时考虑商业影响、修复时效与证据确定性。P0 应在一周内启动，P1 纳入首月增长计划。</p>{issues}</section>

    <section class="section">{section_head("08", "机会地图")}<p>机会分 = 商业价值 35% + 当前缺口 30% + 可实现性 20% + 证据置信度 15%。横轴表示商业价值，纵轴表示可实现性。</p><div class="opp-map">{opportunities}</div></section>

    <section class="section">{section_head("09", "内容与知识资产蓝图")}<p class="lede">每个问题必须落到 <strong>资产、数量、渠道、负责人和验证问题</strong>，避免“加强内容建设”式的空泛建议。</p><div class="table-wrap asset-table"><table><thead><tr><th>优先级</th><th>问题</th><th>需要补充的资产</th><th>数量</th><th>发布渠道</th><th>建议负责人</th><th>验证问题</th><th>成功指标</th></tr></thead><tbody>{asset_rows}</tbody></table></div></section>

    <section class="section">{section_head("10", "30 / 60 / 90 天路线图")}<div class="roadmap">{roadmap}</div></section>

    <section class="section">{section_head("11", "证据目录")}<p>重要事实、评分与策略判断均应能够回溯到来源。缺少原始 URL 的旧报告资料保留来源名称，但不能升级为实时验证。</p><div class="table-wrap evidence-table"><table><thead><tr><th>ID</th><th>事实或判断</th><th>证据状态</th><th>来源</th><th>来源等级</th><th>日期</th><th>支持结论</th></tr></thead><tbody>{evidence_registry_rows}</tbody></table></div></section>

    <section class="section">{section_head("12", "方法与限制")}<div class="evidence-grid">{evidence}</div><ul class="limitations">{limitations}</ul></section>
  </div>
  <footer class="footer"><span>{esc(data["report_title"])} · {esc(data.get("version", "V1.0"))}</span><span>仅基于所列证据，不构成投资建议或商业承诺</span></footer>
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
