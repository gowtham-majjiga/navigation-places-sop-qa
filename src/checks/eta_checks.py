"""
ETA-1 / ETA-2 checks — predicted-vs-actual ETA accuracy and validity.

Each function returns a list of "flag" dicts. A flag dict is the atomic
unit that flows into the logger and the report: it always carries the
rule_id, severity, region, and the exact record_id it came from, so
every flagged row can be traced back to its source policy rule.
"""

from __future__ import annotations

import pandas as pd


def check_invalid_eta(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    """A null/zero/negative ETA is only a defect if the road is NOT
    tagged 'closed' — a closed road legitimately carries no active ETA
    (that's what TRAFFIC-2 checks separately)."""
    severity = rules["eta"]["invalid_eta_severity"]
    flags = []
    numeric_eta = pd.to_numeric(nav_df["actual_eta_min"], errors="coerce")
    invalid = nav_df[
        (numeric_eta.isna() | (numeric_eta <= 0))
        & (nav_df["traffic_flow_tag"] != "closed")
    ]
    for _, row in invalid.iterrows():
        flags.append(
            {
                "rule_id": "ETA-2",
                "rule_desc": "actual ETA must be a positive, non-null value "
                "for any road not tagged 'closed'",
                "severity": severity,
                "category": "eta",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"actual_eta_min={row['actual_eta_min']} traffic_flow_tag={row['traffic_flow_tag']}",
            }
        )
    return flags


def check_eta_deviation(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    threshold_pct = rules["eta"]["eta_deviation_threshold_pct"]
    severity = rules["eta"]["eta_deviation_severity"]
    flags = []

    valid = nav_df.copy()
    valid["actual_eta_min"] = pd.to_numeric(valid["actual_eta_min"], errors="coerce")
    valid = valid[valid["actual_eta_min"] > 0]

    deviation_pct = (
        (valid["actual_eta_min"] - valid["predicted_eta_min"]).abs()
        / valid["predicted_eta_min"]
        * 100
    )
    breached = valid[deviation_pct > threshold_pct]
    breached_dev = deviation_pct[deviation_pct > threshold_pct]

    for (_, row), dev in zip(breached.iterrows(), breached_dev):
        flags.append(
            {
                "rule_id": "ETA-1",
                "rule_desc": f"predicted vs actual ETA deviation must be <= {threshold_pct}%",
                "severity": severity,
                "category": "eta",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"predicted={row['predicted_eta_min']}min "
                f"actual={row['actual_eta_min']}min deviation={dev:.1f}%",
            }
        )
    return flags


def run_all(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    return check_invalid_eta(nav_df, rules) + check_eta_deviation(nav_df, rules)
