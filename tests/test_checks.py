import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.checks import eta_checks, lane_checks, places_checks, traffic_checks
from src.rules_engine import load_rules

RULES = load_rules(Path(__file__).resolve().parent.parent / "config" / "sop_rules.yaml")


def test_eta_deviation_flagged():
    df = pd.DataFrame([
        {"record_id": "nav_1", "region": "hyderabad", "predicted_eta_min": 10, "actual_eta_min": 20},
        {"record_id": "nav_2", "region": "hyderabad", "predicted_eta_min": 10, "actual_eta_min": 10.5},
    ])
    flags = eta_checks.check_eta_deviation(df, RULES)
    flagged_ids = {f["record_id"] for f in flags}
    assert "nav_1" in flagged_ids
    assert "nav_2" not in flagged_ids


def test_invalid_eta_flagged():
    df = pd.DataFrame([
        {"record_id": "nav_3", "region": "pune", "traffic_flow_tag": "moderate", "actual_eta_min": -5},
        {"record_id": "nav_4", "region": "pune", "traffic_flow_tag": "moderate", "actual_eta_min": None},
        {"record_id": "nav_5", "region": "pune", "traffic_flow_tag": "moderate", "actual_eta_min": 12},
        {"record_id": "nav_x", "region": "pune", "traffic_flow_tag": "closed", "actual_eta_min": None},
    ])
    flags = eta_checks.check_invalid_eta(df, RULES)
    assert {f["record_id"] for f in flags} == {"nav_3", "nav_4"}


def test_invalid_flow_tag_flagged():
    df = pd.DataFrame([
        {"record_id": "nav_6", "region": "chennai", "traffic_flow_tag": "unknown"},
        {"record_id": "nav_7", "region": "chennai", "traffic_flow_tag": "moderate"},
    ])
    flags = traffic_checks.check_invalid_flow_tag(df, RULES)
    assert {f["record_id"] for f in flags} == {"nav_6"}


def test_missing_directionality_flagged():
    df = pd.DataFrame([
        {"record_id": "lane_1", "region": "delhi-ncr", "road_id": "r1", "lane_directionality": None},
        {"record_id": "lane_2", "region": "delhi-ncr", "road_id": "r2", "lane_directionality": "forward"},
    ])
    flags = lane_checks.check_missing_directionality(df, RULES)
    assert {f["record_id"] for f in flags} == {"lane_1"}


def test_disconnected_segment_flagged():
    df = pd.DataFrame([
        {"record_id": "lane_3", "region": "pune", "road_id": "r3", "connected_to": None, "segment_tag": "through_road"},
        {"record_id": "lane_4", "region": "pune", "road_id": "r4", "connected_to": None, "segment_tag": "dead_end"},
        {"record_id": "lane_5", "region": "pune", "road_id": "r5", "connected_to": "road_9", "segment_tag": "through_road"},
    ])
    flags = lane_checks.check_disconnected_segments(df, RULES)
    assert {f["record_id"] for f in flags} == {"lane_3"}


def test_missing_required_fields_flagged():
    df = pd.DataFrame([
        {"record_id": "poi_1", "region": "bengaluru", "name": None, "category": "cafe", "lat": 12.9, "lon": 77.6, "address": "123 Main Rd"},
        {"record_id": "poi_2", "region": "bengaluru", "name": "X Corner", "category": "cafe", "lat": 12.9, "lon": 77.6, "address": "123 Main Rd"},
    ])
    flags = places_checks.check_missing_required_fields(df, RULES)
    assert {f["record_id"] for f in flags} == {"poi_1"}


def test_bad_coordinates_flagged():
    df = pd.DataFrame([
        {"record_id": "poi_3", "region": "bengaluru", "lat": 999, "lon": 999},
        {"record_id": "poi_4", "region": "bengaluru", "lat": 12.97, "lon": 77.59},
    ])
    flags = places_checks.check_bad_coordinates(df, RULES)
    assert {f["record_id"] for f in flags} == {"poi_3"}


def test_duplicate_pois_flagged():
    df = pd.DataFrame([
        {"record_id": "poi_5", "region": "chennai", "name": "A Corner", "category": "cafe", "lat": 13.0000, "lon": 80.2000},
        {"record_id": "poi_6", "region": "chennai", "name": "A Corner", "category": "cafe", "lat": 13.00005, "lon": 80.20005},
        {"record_id": "poi_7", "region": "chennai", "name": "A Corner", "category": "cafe", "lat": 13.05, "lon": 80.25},
    ])
    flags = places_checks.check_duplicate_pois(df, RULES)
    flagged_ids = {f["record_id"] for f in flags}
    assert "poi_6" in flagged_ids
    assert "poi_7" not in flagged_ids
