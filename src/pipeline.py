"""
End-to-end batch pipeline:
  load raw data -> run all SOP checks -> structured log -> weekly report

This is the "batch processing" entry point referenced in the resume
bullet about optimizing for high-speed, high-accuracy repetitive
validation. All checks are vectorized pandas operations (no row-by-row
Python loops on the hot path except where needed for pairwise duplicate
distance, which is grouped down to small clusters first).
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from src.checks import eta_checks, lane_checks, places_checks, traffic_checks
from src.logger import write_flag_log
from src.report_generator import build_weekly_report
from src.rules_engine import load_rules


def load_raw_data(data_dir: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
    data_dir = Path(data_dir)
    return {
        "navigation": pd.read_csv(data_dir / "navigation_records.csv"),
        "lanes": pd.read_csv(data_dir / "lanes_records.csv"),
        "places": pd.read_csv(data_dir / "places_records.csv"),
    }


def run_pipeline(
    data_dir: str | Path = "data/raw",
    config_path: str | Path = "config/sop_rules.yaml",
    log_dir: str | Path = "logs",
    report_dir: str | Path = "reports",
) -> dict:
    start = time.perf_counter()

    rules = load_rules(config_path)
    data = load_raw_data(data_dir)

    flags: list[dict] = []
    flags += eta_checks.run_all(data["navigation"], rules)
    flags += traffic_checks.run_all(data["navigation"], rules)
    flags += lane_checks.run_all(data["lanes"], rules)
    flags += places_checks.run_all(data["places"], rules)

    total_records = sum(len(df) for df in data.values())

    log_path = write_flag_log(flags, log_dir=log_dir)

    elapsed = time.perf_counter() - start
    report_path = build_weekly_report(
        flags=flags,
        total_records_scanned=total_records,
        processing_seconds=elapsed,
        rules=rules,
        report_dir=report_dir,
    )

    return {
        "flags": flags,
        "total_records": total_records,
        "processing_seconds": elapsed,
        "log_path": log_path,
        "report_path": report_path,
    }
