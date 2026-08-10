"""
PLACES-1 / PLACES-2 / PLACES-3 checks — required-field completeness,
plausible coordinates, and duplicate POI detection.
"""

from __future__ import annotations

import math

import pandas as pd


def check_missing_required_fields(places_df: pd.DataFrame, rules: dict) -> list[dict]:
    required = rules["places"]["required_fields"]
    severity = rules["places"]["missing_field_severity"]
    flags = []

    for _, row in places_df.iterrows():
        missing_cols = [c for c in required if pd.isna(row.get(c))]
        if missing_cols:
            flags.append(
                {
                    "rule_id": "PLACES-1",
                    "rule_desc": f"required fields must be present: {required}",
                    "severity": severity,
                    "category": "places",
                    "region": row["region"],
                    "record_id": row["record_id"],
                    "evidence": f"missing_fields={missing_cols}",
                }
            )
    return flags


def check_bad_coordinates(places_df: pd.DataFrame, rules: dict) -> list[dict]:
    lat_lo, lat_hi = rules["places"]["lat_range"]
    lon_lo, lon_hi = rules["places"]["lon_range"]
    severity = rules["places"]["bad_coordinate_severity"]
    flags = []

    bad = places_df[
        (places_df["lat"] < lat_lo)
        | (places_df["lat"] > lat_hi)
        | (places_df["lon"] < lon_lo)
        | (places_df["lon"] > lon_hi)
        | ((places_df["lat"] == 0) & (places_df["lon"] == 0))
    ]
    for _, row in bad.iterrows():
        flags.append(
            {
                "rule_id": "PLACES-2",
                "rule_desc": f"lat must be in {rules['places']['lat_range']}, "
                f"lon in {rules['places']['lon_range']}, and not (0, 0)",
                "severity": severity,
                "category": "places",
                "region": row["region"],
                "record_id": row["record_id"],
                "evidence": f"lat={row['lat']} lon={row['lon']}",
            }
        )
    return flags


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(min(1, math.sqrt(a)))


def check_duplicate_pois(places_df: pd.DataFrame, rules: dict) -> list[dict]:
    """O(n log n) per region: group by (name, category), then compare
    only within each small group instead of an all-pairs O(n^2) scan."""
    max_dist = rules["places"]["duplicate_distance_meters"]
    severity = rules["places"]["duplicate_severity"]
    flags = []

    df = places_df.dropna(subset=["name", "category", "lat", "lon"])
    for (_region, _name, _cat), group in df.groupby(["region", "name", "category"]):
        if len(group) < 2:
            continue
        records = group.to_dict("records")
        seen_flagged = set()
        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                r1, r2 = records[i], records[j]
                dist = _haversine_m(r1["lat"], r1["lon"], r2["lat"], r2["lon"])
                if dist <= max_dist and r2["record_id"] not in seen_flagged:
                    seen_flagged.add(r2["record_id"])
                    flags.append(
                        {
                            "rule_id": "PLACES-3",
                            "rule_desc": f"POIs with same name+category within "
                            f"{max_dist}m are likely duplicates",
                            "severity": severity,
                            "category": "places",
                            "region": r2["region"],
                            "record_id": r2["record_id"],
                            "evidence": f"duplicate_of={r1['record_id']} distance_m={dist:.1f}",
                        }
                    )
    return flags


def run_all(places_df: pd.DataFrame, rules: dict) -> list[dict]:
    return (
        check_missing_required_fields(places_df, rules)
        + check_bad_coordinates(places_df, rules)
        + check_duplicate_pois(places_df, rules)
    )
