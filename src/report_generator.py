"""Weekly insight-reporting module."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def flags_to_dataframe(flags: list[dict]) -> pd.DataFrame:
    if not flags:
        return pd.DataFrame(columns=["rule_id", "rule_desc", "severity", "category", "region", "record_id", "evidence"])
    return pd.DataFrame(flags)


def build_weekly_report(flags: list[dict], total_records_scanned: int, processing_seconds: float,
                        rules: dict, report_dir: str | Path = "reports") -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    df = flags_to_dataframe(flags)
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sla_hours = rules["reporting"]["sla_hours_per_batch"]
    processing_hours = processing_seconds / 3600
    sla_met = processing_hours <= sla_hours
    by_severity = df["severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0)
    by_rule = df["rule_id"].value_counts().sort_values(ascending=False) if not df.empty else pd.Series(dtype=int)
    by_region = df["region"].value_counts().sort_values(ascending=False) if not df.empty else pd.Series(dtype=int)
    by_category = df["category"].value_counts() if not df.empty else pd.Series(dtype=int)
    defect_rate_pct = (len(df) / total_records_scanned * 100) if total_records_scanned else 0.0
    lines = [f"# Weekly Map Data QA Insight Report — {run_date}", "", "## Batch Summary",
             f"- Records scanned: **{total_records_scanned:,}**", f"- Total defects flagged: **{len(df):,}**",
             f"- Overall defect rate: **{defect_rate_pct:.2f}%**",
             f"- Processing time: **{processing_seconds:.2f}s** ({processing_hours:.3f}h) vs. SLA target of {sla_hours}h → **{'MET' if sla_met else 'BREACHED'}**",
             "", "## Defects by Severity", "| Severity | Count |", "|---|---|"]
    for sev in SEVERITY_ORDER: lines.append(f"| {sev} | {int(by_severity.get(sev, 0))} |")
    lines += ["", "## Defects by Category", "| Category | Count |", "|---|---|"]
    for cat, cnt in by_category.items(): lines.append(f"| {cat} | {int(cnt)} |")
    lines += ["", "## Top Rules Triggered", "| Rule ID | Count |", "|---|---|"]
    for rule_id, cnt in by_rule.items(): lines.append(f"| {rule_id} | {int(cnt)} |")
    lines += ["", "## Defects by Region", "| Region | Count |", "|---|---|"]
    for region, cnt in by_region.items(): lines.append(f"| {region} | {int(cnt)} |")
    lines += ["", "## High-Impact Findings (CRITICAL only)"]
    critical = df[df["severity"] == "CRITICAL"] if not df.empty else df
    if critical.empty:
        lines.append("_No CRITICAL-severity defects this run._")
    else:
        lines += ["| Rule ID | Region | Record ID | Evidence |", "|---|---|---|---|"]
        for _, row in critical.head(25).iterrows(): lines.append(f"| {row['rule_id']} | {row['region']} | {row['record_id']} | {row['evidence']} |")
        if len(critical) > 25: lines.append(f"\n_... plus {len(critical) - 25} more CRITICAL records (see full log in logs/)._")
    report_path = report_dir / f"weekly_insight_report_{run_date}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    history_path = Path(rules["reporting"]["history_file"])
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_row = pd.DataFrame([{"run_date": run_date, "records_scanned": total_records_scanned,
        "total_defects": len(df), "defect_rate_pct": round(defect_rate_pct, 3),
        "critical": int(by_severity.get("CRITICAL", 0)), "high": int(by_severity.get("HIGH", 0)),
        "medium": int(by_severity.get("MEDIUM", 0)), "low": int(by_severity.get("LOW", 0)),
        "processing_seconds": round(processing_seconds, 3), "sla_hours_target": sla_hours, "sla_met": sla_met}])
    if history_path.exists(): history_row.to_csv(history_path, mode="a", header=False, index=False)
    else: history_row.to_csv(history_path, index=False)
    return report_path
