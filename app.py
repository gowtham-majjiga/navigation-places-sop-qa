"""Streamlit dashboard for the Navigation & Places SOP Compliance QA Framework."""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from src.pipeline import run_pipeline
from src.report_generator import flags_to_dataframe

st.set_page_config(page_title="Map Data SOP Compliance QA", layout="wide")
st.title("🗺️ Navigation & Places SOP Compliance QA Framework")
st.caption("Rule-based QA over synthetic ETA, traffic, lane, and places data — audited against SOP thresholds defined in config/sop_rules.yaml.")

with st.sidebar:
    st.header("Controls")
    run_now = st.button("▶ Run QA pipeline", use_container_width=True)
    st.markdown("---")
    st.markdown("**Note:** all underlying data is synthetically generated (see `src/data_generator.py`) — this is a portfolio demo, not production map data.")

if "result" not in st.session_state:
    st.session_state["result"] = None

if run_now or st.session_state["result"] is None:
    if not Path("data/raw/navigation_records.csv").exists():
        st.warning("No input data found — generating synthetic datasets first...")
        from src.data_generator import main as generate_data
        generate_data()
    with st.spinner("Running SOP checks across ETA, traffic, lanes, and places..."):
        st.session_state["result"] = run_pipeline()

result = st.session_state["result"]
flags_df = flags_to_dataframe(result["flags"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Records scanned", f"{result['total_records']:,}")
col2.metric("Defects flagged", f"{len(flags_df):,}")
defect_rate = (len(flags_df) / result["total_records"] * 100) if result["total_records"] else 0
col3.metric("Defect rate", f"{defect_rate:.2f}%")
col4.metric("Processing time", f"{result['processing_seconds']:.2f}s")

st.markdown("---")
left, right = st.columns(2)
with left:
    st.subheader("Defects by Severity")
    if not flags_df.empty:
        sev_counts = flags_df["severity"].value_counts().reindex(["CRITICAL", "HIGH", "MEDIUM", "LOW"], fill_value=0)
        st.bar_chart(sev_counts)
    else: st.info("No defects flagged in this run.")
with right:
    st.subheader("Defects by Region")
    if not flags_df.empty: st.bar_chart(flags_df["region"].value_counts())
    else: st.info("No defects flagged in this run.")

st.subheader("Defects by Rule ID")
if not flags_df.empty: st.bar_chart(flags_df["rule_id"].value_counts())

st.subheader("Anomaly Trend Across Runs")
history_path = Path("reports/history.csv")
if history_path.exists():
    history_df = pd.read_csv(history_path)
    st.line_chart(history_df.set_index("run_date")[["critical", "high", "medium", "low"]])
else: st.info("Run the pipeline a few times to build up trend history.")

st.subheader("Flagged Records")
if not flags_df.empty:
    severity_filter = st.multiselect("Filter by severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH"])
    region_filter = st.multiselect("Filter by region", sorted(flags_df["region"].unique()), default=[])
    filtered = flags_df[flags_df["severity"].isin(severity_filter)] if severity_filter else flags_df
    if region_filter: filtered = filtered[filtered["region"].isin(region_filter)]
    st.dataframe(filtered, use_container_width=True, height=400)
else: st.info("No flagged records to display.")

st.markdown("---")
st.caption(f"Weekly report written to: `{result['report_path']}`")
