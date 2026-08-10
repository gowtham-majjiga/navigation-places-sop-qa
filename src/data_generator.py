"""
Synthetic data generator for the Navigation & Places SOP Compliance QA
Framework.

Real map/navigation data (ETA telemetry, lane graphs, POI catalogs) is
proprietary, so this generator produces realistic *synthetic* datasets
with injected, controllable defect rates. This keeps the project fully
reproducible and safe to publish publicly while still exercising every
rule in config/sop_rules.yaml.

Run directly:  python -m src.data_generator
"""

from __future__ import annotations

import random
import string
from pathlib import Path

import pandas as pd

REGIONS = ["hyderabad", "bengaluru", "chennai", "delhi-ncr", "pune"]
TRAFFIC_TAGS_VALID = ["free_flow", "moderate", "heavy", "closed"]
TRAFFIC_TAGS_BAD = ["freeflow", "HEAVY!!", "", "unknown"]
DIRECTIONALITY_VALID = ["forward", "backward", "bidirectional"]
PLACE_CATEGORIES = ["restaurant", "fuel_station", "hospital", "atm", "school", "cafe"]

RNG = random.Random(42)


def _rand_id(prefix: str, n: int) -> str:
    return f"{prefix}_{n:06d}"


def _rand_road_ids(region: str, count: int) -> list[str]:
    return [f"{region}_road_{i:04d}" for i in range(count)]


def generate_navigation_records(n_per_region: int = 400) -> pd.DataFrame:
    rows = []
    rec_no = 0
    for region in REGIONS:
        road_ids = _rand_road_ids(region, n_per_region // 2)
        for _ in range(n_per_region):
            rec_no += 1
            predicted = round(RNG.uniform(3, 45), 1)
            if RNG.random() < 0.12:
                actual = round(predicted * RNG.choice([1.4, 1.6, 0.5, 0.6]), 1)
            else:
                actual = round(predicted * RNG.uniform(0.92, 1.08), 1)
            if RNG.random() < 0.02:
                actual = RNG.choice([-1, 0, None])
            flow_tag = RNG.choice(TRAFFIC_TAGS_BAD) if RNG.random() < 0.06 else RNG.choice(TRAFFIC_TAGS_VALID)
            if flow_tag == "closed" and RNG.random() > 0.15:
                actual = None
            rows.append({
                "record_id": _rand_id("nav", rec_no), "region": region,
                "road_id": RNG.choice(road_ids), "predicted_eta_min": predicted,
                "actual_eta_min": actual, "traffic_flow_tag": flow_tag,
                "timestamp": pd.Timestamp("2026-06-01") + pd.Timedelta(minutes=RNG.randint(0, 60 * 24 * 7)),
            })
    return pd.DataFrame(rows)


def generate_lane_records(n_per_region: int = 250) -> pd.DataFrame:
    rows = []
    rec_no = 0
    for region in REGIONS:
        road_ids = _rand_road_ids(region, n_per_region)
        for i, road_id in enumerate(road_ids):
            rec_no += 1
            directionality = None if RNG.random() < 0.08 else RNG.choice(DIRECTIONALITY_VALID)
            lane_count = RNG.choice([1, 2, 2, 3, 4])
            if RNG.random() < 0.03:
                lane_count = RNG.choice([0, -1, 12])
            is_dead_end = RNG.random() < 0.1
            if is_dead_end:
                connected_to, tag = None, "dead_end"
            elif RNG.random() < 0.07:
                connected_to, tag = None, "through_road"
            else:
                connected_to, tag = road_ids[(i + 1) % len(road_ids)], "through_road"
            rows.append({
                "record_id": _rand_id("lane", rec_no), "region": region,
                "road_id": road_id, "lane_count": lane_count,
                "lane_directionality": directionality, "connected_to": connected_to,
                "segment_tag": tag,
            })
    return pd.DataFrame(rows)


def generate_places_records(n_per_region: int = 300) -> pd.DataFrame:
    rows = []
    rec_no = 0
    region_bounds = {
        "hyderabad": (17.2, 17.6, 78.2, 78.6), "bengaluru": (12.8, 13.2, 77.4, 77.8),
        "chennai": (12.9, 13.2, 80.1, 80.3), "delhi-ncr": (28.4, 28.9, 76.9, 77.4),
        "pune": (18.4, 18.7, 73.7, 74.0),
    }
    for region in REGIONS:
        lat_min, lat_max, lon_min, lon_max = region_bounds[region]
        used_signatures = []
        for _ in range(n_per_region):
            rec_no += 1
            name = "".join(RNG.choices(string.ascii_uppercase, k=1)) + " " + RNG.choice(["Corner", "Plaza", "Store", "Point", "Center", "Junction"])
            category = RNG.choice(PLACE_CATEGORIES)
            lat, lon = round(RNG.uniform(lat_min, lat_max), 5), round(RNG.uniform(lon_min, lon_max), 5)
            if used_signatures and RNG.random() < 0.10:
                name, category, lat, lon = RNG.choice(used_signatures)
                lat, lon = round(lat + RNG.uniform(-0.0002, 0.0002), 5), round(lon + RNG.uniform(-0.0002, 0.0002), 5)
            else:
                used_signatures.append((name, category, lat, lon))
            if RNG.random() < 0.02:
                lat, lon = RNG.choice([(999, 999), (-999, 200), (0, 0)])
            address = f"{RNG.randint(1, 200)} Main Road, {region.title()}"
            if RNG.random() < 0.05: name = None
            if RNG.random() < 0.05: address = None
            rows.append({
                "record_id": _rand_id("poi", rec_no), "region": region,
                "place_id": _rand_id(f"{region}_poi", rec_no), "name": name,
                "category": category, "lat": lat, "lon": lon, "address": address,
            })
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    nav_df, lane_df, places_df = generate_navigation_records(), generate_lane_records(), generate_places_records()
    nav_df.to_csv(out_dir / "navigation_records.csv", index=False)
    lane_df.to_csv(out_dir / "lanes_records.csv", index=False)
    places_df.to_csv(out_dir / "places_records.csv", index=False)
    print(f"Wrote {len(nav_df)} navigation records -> {out_dir / 'navigation_records.csv'}")
    print(f"Wrote {len(lane_df)} lane records -> {out_dir / 'lanes_records.csv'}")
    print(f"Wrote {len(places_df)} places records -> {out_dir / 'places_records.csv'}")


if __name__ == "__main__":
    main()
