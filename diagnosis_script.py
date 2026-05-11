"""
========================================================
PROJECT 2 — Process Emissions Diagnostic & Optimization
========================================================

Purpose:
--------
Generate simulated industrial emissions/process data,
perform analysis, and export clean CSV files for Streamlit.

Workflow:
---------
1. Generate synthetic process + emissions data
2. Detect anomalies and compliance gaps
3. Calculate KPIs automatically
4. Export reusable CSV files
5. Streamlit dashboard reads exported files

Run:
----
python analysis.py
"""

# ======================================================
# 1. IMPORT LIBRARIES
# ======================================================

import pandas as pd
import numpy as np
from pathlib import Path

# Make random numbers reproducible
np.random.seed(42)

# ======================================================
# 2. CREATE OUTPUT FOLDER
# ======================================================

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# ======================================================
# 3. GENERATE SYNTHETIC DATA
# ======================================================

days = 365

dates = pd.date_range(
    start="2024-01-01",
    periods=days,
    freq="D"
)

# ------------------------------------------------------
# Production rate (%)
# Seasonal production behavior
# ------------------------------------------------------

production_rate = (
    75
    + 12 * np.sin(np.linspace(0, 2 * np.pi, days))
    + np.random.normal(0, 4, days)
)

production_rate = np.clip(production_rate, 55, 100)

# ------------------------------------------------------
# Burner load (%)
# Normally follows production
# ------------------------------------------------------

burner_load = (
    production_rate
    + np.random.normal(0, 3, days)
)

burner_load = np.clip(burner_load, 50, 100)

# ------------------------------------------------------
# Oxygen (O2 %) readings
# Slightly stable during anomaly period
# ------------------------------------------------------

o2 = (
    5
    + np.random.normal(0, 0.3, days)
)

# Create suspiciously stable O2 period
o2[160:240] = 5 + np.random.normal(0, 0.05, 80)

# ------------------------------------------------------
# Process temperature
# Depends on burner load
# ------------------------------------------------------

temperature = (
    780
    + burner_load * 1.2
    + np.random.normal(0, 8, days)
)

# ------------------------------------------------------
# CO emissions
# Main anomaly parameter
# ------------------------------------------------------

co = (
    300
    + np.random.normal(0, 25, days)
)

# Create anomaly window
co[160:240] += np.linspace(40, 160, 80)

# ------------------------------------------------------
# Online sensor values
# Wrong correction factor applied
# Appears artificially low
# ------------------------------------------------------

online_emissions = co * 0.5

# ------------------------------------------------------
# Audit measurements
# Real values measured externally
# ------------------------------------------------------

audit_measurements = co * 1.02

# ------------------------------------------------------
# Compliance limit
# ------------------------------------------------------

CO_LIMIT = 400

# ======================================================
# 4. CREATE MAIN DATAFRAME
# ======================================================

df = pd.DataFrame({

    "date": dates,

    "production_rate_pct": production_rate.round(1),

    "burner_load_pct": burner_load.round(1),

    "o2_pct": o2.round(2),

    "temperature_C": temperature.round(1),

    "online_CO_mg_Nm3": online_emissions.round(1),

    "audit_CO_mg_Nm3": audit_measurements.round(1)

})

# ======================================================
# 5. CREATE ANALYSIS FLAGS
# ======================================================

# Online system exceedance
df["online_exceed"] = (
    df["online_CO_mg_Nm3"] > CO_LIMIT
)

# Audit exceedance
df["audit_exceed"] = (
    df["audit_CO_mg_Nm3"] > CO_LIMIT
)

# Anomaly period flag
df["anomaly_period"] = False
df.loc[160:240, "anomaly_period"] = True

# ======================================================
# 6. KPI CALCULATIONS
# ======================================================

# Number of exceedances
audit_exceedances = int(df["audit_exceed"].sum())

# Compliance rate
compliance_rate = round(
    (
        1
        - audit_exceedances / len(df)
    ) * 100,
    1
)

# Sensor discrepancy ratio
avg_online = df["online_CO_mg_Nm3"].mean()
avg_audit = df["audit_CO_mg_Nm3"].mean()

discrepancy_ratio = round(
    avg_audit / avg_online,
    2
)

# Correlation between O2 and CO
correlation_o2_co = round(
    df["o2_pct"].corr(df["audit_CO_mg_Nm3"]),
    2
)

# ======================================================
# 7. KPI TABLE
# ======================================================

kpis = pd.DataFrame({

    "metric": [

        "Audit exceedances",
        "Compliance rate",
        "Average online CO",
        "Average audit CO",
        "Sensor discrepancy ratio",
        "O2 vs CO correlation"

    ],

    "value": [

        audit_exceedances,
        compliance_rate,
        round(avg_online, 1),
        round(avg_audit, 1),
        discrepancy_ratio,
        correlation_o2_co

    ]

})

# ======================================================
# 8. MONTHLY ANALYSIS
# ======================================================

df["month"] = df["date"].dt.to_period("M")

monthly = df.groupby("month").agg(

    mean_online_CO=("online_CO_mg_Nm3", "mean"),

    mean_audit_CO=("audit_CO_mg_Nm3", "mean"),

    exceedances=("audit_exceed", "sum"),

    mean_O2=("o2_pct", "mean"),

    mean_burner_load=("burner_load_pct", "mean")

).round(1)

# ======================================================
# 9. CORRELATION MATRIX
# ======================================================

corr_columns = [

    "production_rate_pct",
    "burner_load_pct",
    "o2_pct",
    "temperature_C",
    "audit_CO_mg_Nm3"

]

correlation_matrix = (
    df[corr_columns]
    .corr()
    .round(2)
)

# ======================================================
# 10. ROOT CAUSE SUMMARY TABLE
# ======================================================

root_causes = pd.DataFrame({

    "Issue": [

        "Pressure leak",
        "Wrong correction factor",
        "Incomplete combustion"

    ],

    "Evidence": [

        "Stable O2 despite CO increase",

        "Audit values consistently higher",

        "CO increased despite high burner load"

    ],

    "Impact": [

        "Diluted sensor readings",

        "Underreported emissions",

        "Real emissions exceedance"

    ]

})

# ======================================================
# 11. EXPORT FILES
# ======================================================

df.to_csv(
    output_dir / "process_data.csv",
    index=False
)

monthly.to_csv(
    output_dir / "monthly_summary.csv"
)

correlation_matrix.to_csv(
    output_dir / "correlation_matrix.csv"
)

kpis.to_csv(
    output_dir / "kpis.csv",
    index=False
)

root_causes.to_csv(
    output_dir / "root_causes.csv",
    index=False
)

# ======================================================
# 12. TERMINAL SUMMARY
# ======================================================

print("\n========================================")
print("PROJECT 2 ANALYSIS COMPLETE")
print("========================================")

print(f"\nAudit exceedances: {audit_exceedances}")

print(f"Compliance rate: {compliance_rate}%")

print(f"Sensor discrepancy ratio: {discrepancy_ratio}")

print(f"O2 vs CO correlation: {correlation_o2_co}")

print("\nFiles exported to /output folder")

print("\nGenerated files:")
print("- process_data.csv")
print("- monthly_summary.csv")
print("- correlation_matrix.csv")
print("- kpis.csv")
print("- root_causes.csv")

print("\n========================================")
