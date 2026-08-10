"""Loads and validates the SOP rules config that drives every check."""

from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED_SECTIONS = ["eta", "traffic", "lanes", "places", "reporting"]


def load_rules(path: str | Path = "config/sop_rules.yaml") -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"SOP rules file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)

    missing = [s for s in REQUIRED_SECTIONS if s not in rules]
    if missing:
        raise ValueError(f"sop_rules.yaml is missing required section(s): {missing}")

    return rules
