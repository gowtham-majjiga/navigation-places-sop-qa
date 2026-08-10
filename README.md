# Navigation & Places SOP Compliance QA Framework

A rule-based QA pipeline that audits **navigation, traffic, lane-level, and places (POI) map data** against defined SOPs and policy thresholds — flagging anomalies, scoring severity, and generating weekly insight reports for stakeholder review. Built to mirror the kind of map-defect investigation workflow used in production map-quality teams (ETA accuracy, traffic-flow tagging, lane connectivity, POI completeness).

> **Note on data:** real navigation/map telemetry is proprietary, so this project uses a deterministic **synthetic data generator** with controllable, injected defect rates (see `src/data_generator.py`). Every check is written against realistic field definitions and thresholds, so the logic transfers directly to real map data — only the input source changes.

## What it does

| Domain | Checks | Rule IDs |
|---|---|---|
| **ETA** | predicted-vs-actual deviation threshold, invalid/null ETA | `ETA-1`, `ETA-2` |
| **Traffic** | invalid flow tags, speed/traffic consistency | `TRAFFIC-1`, `TRAFFIC-2` |
| **Lanes** | connectivity, direction, lane-count consistency | `LANE-1`, `LANE-2` |
| **Places** | missing/duplicate POI attributes and category issues | `PLACE-1`, `PLACE-2` |

## Pipeline

`Synthetic Data → Rule Checks → Severity Scoring → Structured Logs → Weekly Insight Report`

The framework is modular so new checks can be added without changing the pipeline orchestration.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Run tests with:

```bash
pytest -q
```

## Project structure

```text
.
├── app.py
├── main.py
├── config/sop_rules.yaml
├── data/raw/
├── reports/
├── logs/
├── src/
│   ├── checks/
│   ├── data_generator.py
│   ├── pipeline.py
│   ├── report_generator.py
│   ├── rules_engine.py
│   └── logger.py
└── tests/
```

## Portfolio relevance

This project demonstrates practical data-quality engineering: deterministic test-data generation, rule-based anomaly detection, configurable SOP thresholds, severity classification, audit logging, automated reporting, and test coverage. It is designed to resemble a production QA workflow for map/navigation data while remaining reproducible with synthetic data.
