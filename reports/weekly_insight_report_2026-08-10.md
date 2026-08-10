# Weekly Map Data QA Insight Report — 2026-08-10

## Batch Summary
- Records scanned: **4,750**
- Total defects flagged: **980**
- Overall defect rate: **20.63%**
- Processing time: **0.37s** (0.000h) vs. SLA target of 4h → **MET**

## Defects by Severity
| Severity | Count |
|---|---|
| CRITICAL | 160 |
| HIGH | 378 |
| MEDIUM | 442 |
| LOW | 0 |

## Defects by Category
| Category | Count |
|---|---|
| places | 321 |
| lanes | 231 |
| eta | 227 |
| traffic | 201 |

## Top Rules Triggered
| Rule ID | Count |
|---|---|
| ETA-1 | 190 |
| PLACES-1 | 153 |
| PLACES-3 | 133 |
| TRAFFIC-1 | 118 |
| LANES-1 | 105 |
| LANES-2 | 88 |
| TRAFFIC-2 | 83 |
| LANES-3 | 38 |
| ETA-2 | 37 |
| PLACES-2 | 35 |

## Defects by Region
| Region | Count |
|---|---|
| bengaluru | 209 |
| pune | 203 |
| chennai | 190 |
| delhi-ncr | 190 |
| hyderabad | 188 |

## High-Impact Findings (CRITICAL only)

The sample run recorded 160 CRITICAL findings. The full structured JSONL log is intentionally excluded from Git history because it is regenerated on demand. Run `python main.py --generate-data --run` to reproduce a fresh audit.
