import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "asset_age_days", "cpu_usage", "memory_usage", "disk_usage", "temperature",
    "network_load", "error_count", "uptime_hours", "previous_failure_count",
    "days_since_maintenance", "previous_maintenance_count", "maintenance_cost",
    "criticality_score"
]

def build_features(df):
    data = df.copy()
    for c in FEATURE_COLUMNS:
        data[c] = pd.to_numeric(data[c], errors="coerce").fillna(0)
    data["criticality_score"] = data["criticality_score"].clip(1, 5)
    return data[FEATURE_COLUMNS]
