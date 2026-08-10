"""
TRAFFIC-1 / TRAFFIC-2 checks — traffic-flow tag vocabulary and
closed-road/active-ETA consistency.
"""

from __future__ import annotations

import pandas as pd


def check_invalid_flow_tag(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    valid_tags = set(rules["traffic"]["valid_flow_tags"])
    severity = rules["traffic"]["invalid_tag_severity"]
    flags = []

    invalid = nav_df[~nav_df["traffic_flow_tag"].isin(valid_tags)]
    for _, row in invalid.iterrows():
        flags.append(
            {
                "rule_id": "TRAFFIC-1",
                "rule_desc": f"traffic_flow_tag must be one of {sorted(valid_tags)}",
                "severity": severity,
                "category": "traffic",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"traffic_flow_tag={row['traffic_flow_tag']!r}",
            }
        )
    return flags


def check_closed_road_with_active_eta(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    severity = rules["traffic"]["closed_road_with_eta_severity"]
    flags = []

    closed = nav_df[nav_df["traffic_flow_tag"] == "closed"]
    active = closed[pd.to_numeric(closed["actual_eta_min"], errors="coerce") > 0]
    for _, row in active.iterrows():
        flags.append(
            {
                "rule_id": "TRAFFIC-2",
                "rule_desc": "a road tagged 'closed' must not carry an active ETA record",
                "severity": severity,
                "category": "traffic",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"road_id={row['road_id']} actual_eta_min={row['actual_eta_min']}",
            }
        )
    return flags


def run_all(nav_df: pd.DataFrame, rules: dict) -> list[dict]:
    return check_invalid_flow_tag(nav_df, rules) + check_closed_road_with_active_eta(
        nav_df, rules
    )
