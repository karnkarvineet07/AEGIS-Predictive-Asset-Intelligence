import joblib
from pathlib import Path
from datetime import date
from db import query
from ml.feature_engineering import build_features

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "failure_prediction_model.pkl"

def _feature_row(asset_id):
    sql = """
    SELECT a.asset_id,
      DATEDIFF(CURDATE(), a.installation_date) asset_age_days,
      COALESCE(m.cpu_usage,0) cpu_usage, COALESCE(m.memory_usage,0) memory_usage,
      COALESCE(m.disk_usage,0) disk_usage, COALESCE(m.temperature,0) temperature,
      COALESCE(m.network_load,0) network_load, COALESCE(m.error_count,0) error_count,
      COALESCE(m.uptime_hours,0) uptime_hours,
      (SELECT COUNT(*) FROM failures f WHERE f.asset_id=a.asset_id AND f.failure_date < CURDATE()) previous_failure_count,
      COALESCE(DATEDIFF(CURDATE(), (SELECT MAX(ma.maintenance_date) FROM maintenance ma WHERE ma.asset_id=a.asset_id)),365) days_since_maintenance,
      (SELECT COUNT(*) FROM maintenance ma2 WHERE ma2.asset_id=a.asset_id AND ma2.maintenance_date <= CURDATE()) previous_maintenance_count,
      COALESCE((SELECT AVG(ma3.cost) FROM maintenance ma3 WHERE ma3.asset_id=a.asset_id AND ma3.maintenance_date <= CURDATE()),0) maintenance_cost,
      CASE a.criticality WHEN 'CRITICAL' THEN 5 WHEN 'HIGH' THEN 4 WHEN 'MEDIUM' THEN 3 ELSE 2 END criticality_score
    FROM assets a
    LEFT JOIN (
      SELECT am.* FROM asset_metrics am
      INNER JOIN (SELECT asset_id, MAX(recorded_at) mx FROM asset_metrics GROUP BY asset_id) x
      ON x.asset_id=am.asset_id AND x.mx=am.recorded_at
    ) m ON m.asset_id=a.asset_id
    WHERE a.asset_id=%s
    """
    return query(sql,(asset_id,),"one")

def predict_asset(asset_id):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("ML model is unavailable. Run python -m ml.train_model after loading seed data.")
    row = _feature_row(asset_id)
    if not row: raise ValueError("Asset not found.")
    bundle = joblib.load(MODEL_PATH)
    X = build_features(__import__("pandas").DataFrame([row]))
    probability = float(bundle["model"].predict_proba(X)[0,1])
    risk = "HIGH" if probability >= .70 else ("MEDIUM" if probability >= .40 else "LOW")
    health = max(0, min(100, round(100 - probability*100)))
    rec = {
        "HIGH":"Schedule preventive maintenance immediately and inspect critical components.",
        "MEDIUM":"Inspect the asset within the next 7 days and continue close monitoring.",
        "LOW":"Continue normal monitoring and follow the planned maintenance schedule."
    }[risk]
    factors = []
    if row["temperature"] >= 70: factors.append("High temperature")
    if row["error_count"] >= 20: factors.append("High error count")
    if row["days_since_maintenance"] >= 120: factors.append("Long maintenance gap")
    if row["cpu_usage"] >= 85: factors.append("High CPU utilization")
    if row["previous_failure_count"] >= 2: factors.append("Previous failures")
    if row["memory_usage"] >= 85: factors.append("High memory utilization")
    if not factors: factors.append("No dominant abnormal factor; continue monitoring")
    query("""INSERT INTO predictions
        (asset_id,prediction_date,failure_probability,risk_level,health_score,recommendation,model_version)
        VALUES (%s,CURDATE(),%s,%s,%s,%s,%s)""",
        (asset_id, probability, risk, health, rec, bundle.get("model_name","model")), commit=True)
    return {"asset_id":asset_id,"probability":probability,"risk":risk,"health_score":health,
            "recommendation":rec,"factors":factors,"model":bundle.get("model_name")}

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("asset_id",type=int)
    args=p.parse_args()
    print(predict_asset(args.asset_id))
