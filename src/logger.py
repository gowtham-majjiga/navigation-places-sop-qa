"""
Structured logging for the QA pipeline.

Every flagged record is written as one JSON line so that any record
can be traced back to the exact rule_id (and the rule's plain-English
description from sop_rules.yaml) that flagged it — this is what makes
the pipeline auditable rather than a black box.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_flag_log(flags: list[dict], log_dir: str | Path = "logs") -> Path:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"qa_run_{run_ts}.jsonl"

    with log_path.open("w", encoding="utf-8") as f:
        for flag in flags:
            record = {**flag, "logged_at": datetime.now(timezone.utc).isoformat()}
            f.write(json.dumps(record) + "\n")

    return log_path
