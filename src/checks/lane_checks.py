"""
LANES-1 / LANES-2 / LANES-3 checks — directionality, connectivity, and
lane-count sanity for lane-level map data.
"""

from __future__ import annotations

import pandas as pd


def check_missing_directionality(lane_df: pd.DataFrame, rules: dict) -> list[dict]:
    severity = rules["lanes"]["missing_directionality_severity"]
    flags = []

    missing = lane_df[lane_df["lane_directionality"].isna()]
    for _, row in missing.iterrows():
        flags.append(
            {
                "rule_id": "LANES-1",
                "rule_desc": "every lane record must declare a directionality",
                "severity": severity,
                "category": "lanes",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"road_id={row['road_id']} lane_directionality=None",
            }
        )
    return flags


def check_disconnected_segments(lane_df: pd.DataFrame, rules: dict) -> list[dict]:
    exempt_tag = rules["lanes"]["require_connectivity_unless_tagged"]
    severity = rules["lanes"]["disconnected_segment_severity"]
    flags = []

    disconnected = lane_df[
        lane_df["connected_to"].isna() & (lane_df["segment_tag"] != exempt_tag)
    ]
    for _, row in disconnected.iterrows():
        flags.append(
            {
                "rule_id": "LANES-2",
                "rule_desc": f"non-'{exempt_tag}' segments must connect to another road_id",
                "severity": severity,
                "category": "lanes",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"road_id={row['road_id']} segment_tag={row['segment_tag']}",
            }
        )
    return flags


def check_lane_count_range(lane_df: pd.DataFrame, rules: dict) -> list[dict]:
    lo, hi = rules["lanes"]["min_lane_count"], rules["lanes"]["max_lane_count"]
    severity = rules["lanes"]["lane_count_severity"]
    flags = []

    bad = lane_df[(lane_df["lane_count"] < lo) | (lane_df["lane_count"] > hi)]
    for _, row in bad.iterrows():
        flags.append(
            {
                "rule_id": "LANES-3",
                "rule_desc": f"lane_count must be between {lo} and {hi}",
                "severity": severity,
                "category": "lanes",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"road_id={row['road_id']} lane_count={row['lane_count']}",
            }
        )
    return flags


def run_all(lane_df: pd.DataFrame, rules: dict) -> list[dict]:
    return (
        check_missing_directionality(lane_df, rules)
        + check_disconnected_segments(lane_df, rules)
        + check_lane_count_range(lane_df, rules)
    )
