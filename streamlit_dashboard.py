"""
========================================================
PROJECT 2 — STREAMLIT DASHBOARD
========================================================

Purpose:
--------
Visualize emissions diagnostic analysis exported
from analysis.py

Run:
----
streamlit run dashboard.py
"""

# ======================================================
# 1. IMPORT LIBRARIES
# ======================================================

from hyperlink import URL
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================================================
# 2. PAGE SETTINGS
# ======================================================

st.set_page_config(
    page_title="Process Emissions Diagnostic",
    layout="wide"
)

# ======================================================
# 3. LOAD DATA
# ======================================================

df = pd.read_csv("output/process_data.csv")

monthly = pd.read_csv("output/monthly_summary.csv")

corr = pd.read_csv("output/correlation_matrix.csv")

kpis = pd.read_csv("output/kpis.csv")

root_causes = pd.read_csv("output/root_causes.csv")

# ======================================================
# 4. HEADER
# ======================================================

st.title("Process Emissions Diagnostic")

st.markdown("""
Industrial emissions diagnostic investigation using
process signals and emissions data.
""")

# ======================================================
# 5. KPI SECTION (STYLED CARDS)
# ======================================================

st.subheader("Key Performance Indicators")

# Safety fix: avoid NaN or weird types
kpis = kpis.fillna(0)

# Create columns dynamically based on KPI count
cols = st.columns(len(kpis))

for i, row in kpis.iterrows():
    metric = row["metric"]
    value = float(row["value"])

    # ✅ DETERMINE CARD COLOR BASED ON VALUE THRESHOLDS
    # Used for both value text and card styling (green/orange/red)
    if value > 80:
        color = "#16a34a"       # green - good performance
        bg = "#ecfdf5"          # light green background
    elif value > 50:
        color = "#d97706"       # orange - moderate performance
        bg = "#fffbeb"          # light orange background
    else:
        color = "#dc2626"       # red - needs attention
        bg = "#fef2f2"          # light red background

    # ✅ CREATE STYLED KPI CARD WITH FIXED HEIGHT & FLEXIBLE LAYOUT
    # Key improvements:
    # - height: 120px keeps all cards uniform (prevents size differences)
    # - white-space: nowrap prevents metric name from wrapping
    # - Flexbox (flex-direction, justify-content) centers content vertically
    # - Heading color now matches value color for visual consistency
    # - font-size increased: heading 13px -> value 36px (was 32px)
    card_html = f"""
    <div style="
        background-color: {bg};
        border-left: 5px solid {color};
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    ">
        <p style="
            margin: 0;
            font-size: 13px;
            color: {color};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        ">
            {metric}
        </p>
        <p style="margin: 8px 0 0 0; font-size: 36px; font-weight: bold; color: {color};">
            {value:.1f}
        </p>
    </div>
    """

    with cols[i]:
        st.markdown(card_html, unsafe_allow_html=True)
# ======================================================
# 6. ONLINE VS AUDIT CHART
# ======================================================

st.subheader("Online Sensor vs Audit Measurements")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    df["online_CO_mg_Nm3"],
    label="Online Sensor"
)

ax.plot(
    df["audit_CO_mg_Nm3"],
    label="Audit Measurement"
)

ax.axhline(
    400,
    linestyle="--",
    label="Compliance Limit"
)

ax.set_ylabel("CO mg/Nm3")

ax.legend()

st.pyplot(fig)

# ======================================================
# 7. CO ANOMALY CHART
# ======================================================

st.subheader("CO Emissions During Anomaly Period")

fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(
    df["audit_CO_mg_Nm3"],
    linewidth=1
)

ax.set_ylabel("Audit CO")

st.pyplot(fig)

# ======================================================
# 8. O2 VS CO SCATTER
# ======================================================

st.subheader("O2 vs CO Correlation")

fig, ax = plt.subplots(figsize=(7, 5))

ax.scatter(

    df["o2_pct"],

    df["audit_CO_mg_Nm3"],

    alpha=0.6

)

ax.set_xlabel("O2 %")

ax.set_ylabel("Audit CO")

st.pyplot(fig)

# ======================================================
# 9. MONTHLY SUMMARY TABLE
# ======================================================

st.subheader("Monthly Summary")

st.dataframe(monthly)

# ======================================================
# 10. CORRELATION MATRIX
# ======================================================

st.subheader("Correlation Matrix")

st.dataframe(corr)

# ======================================================
# 11. ROOT CAUSE TABLE
# ======================================================

st.subheader("Root Cause Analysis")

st.dataframe(root_causes)

# ======================================================
# 12. FINAL INSIGHT
# ======================================================

st.info("""

Main finding:

The emissions issue was NOT caused by production rate
alone.

Cross-parameter analysis showed:
- incorrect sensor correction factor
- pressure leak dilution
- incomplete combustion behavior

This explains why audit measurements were much higher
than online sensor readings.

""")

