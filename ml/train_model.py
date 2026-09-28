"""Train failure-prediction models from historical telemetry snapshots without target leakage."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from db import get_connection
from ml.feature_engineering import build_features, FEATURE_COLUMNS

SQL = """
SELECT am.asset_id, am.recorded_at,
  DATEDIFF(DATE(am.recorded_at), a.installation_date) AS asset_age_days,
  am.cpu_usage, am.memory_usage, am.disk_usage, am.temperature, am.network_load,
  am.error_count, am.uptime_hours,
  (SELECT COUNT(*) FROM failures f WHERE f.asset_id=am.asset_id AND f.failure_date < DATE(am.recorded_at)) AS previous_failure_count,
  COALESCE(DATEDIFF(DATE(am.recorded_at), (SELECT MAX(ma.maintenance_date) FROM maintenance ma WHERE ma.asset_id=am.asset_id AND ma.maintenance_date <= DATE(am.recorded_at))),365) AS days_since_maintenance,
  (SELECT COUNT(*) FROM maintenance ma2 WHERE ma2.asset_id=am.asset_id AND ma2.maintenance_date <= DATE(am.recorded_at)) AS previous_maintenance_count,
  COALESCE((SELECT AVG(ma3.cost) FROM maintenance ma3 WHERE ma3.asset_id=am.asset_id AND ma3.maintenance_date <= DATE(am.recorded_at)),0) AS maintenance_cost,
  CASE a.criticality WHEN 'CRITICAL' THEN 5 WHEN 'HIGH' THEN 4 WHEN 'MEDIUM' THEN 3 ELSE 2 END AS criticality_score,
  CASE WHEN EXISTS (SELECT 1 FROM failures f2 WHERE f2.asset_id=am.asset_id
                    AND f2.failure_date > DATE(am.recorded_at)
                    AND f2.failure_date <= DATE_ADD(DATE(am.recorded_at), INTERVAL 30 DAY))
       THEN 1 ELSE 0 END AS failure_within_30_days
FROM asset_metrics am JOIN assets a ON a.asset_id=am.asset_id
WHERE a.status <> 'RETIRED'
"""

def main():
    from app import app

    with app.app_context():
        conn = get_connection()
        df = pd.read_sql(SQL, conn)
        conn.close()
    if len(df)<40 or df["failure_within_30_days"].nunique()<2:
        raise RuntimeError("Not enough historical snapshots with both failure classes. Import seed.sql first.")
    y=df.pop("failure_within_30_days").astype(int)
    X=build_features(df)
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25,random_state=42,stratify=y)
    # Oversample the minority class in TRAINING ONLY; the untouched test set remains representative.
    train=pd.concat([X_train.assign(_target=y_train.values),],axis=1)
    pos=train[train._target==1]
    if len(pos)>0 and len(pos)<50:
        extra=pos.sample(n=max(0,50-len(pos)),replace=True,random_state=42).drop(columns=["_target"])
        noise=extra.copy()
        for c in ["cpu_usage","memory_usage","disk_usage","temperature","network_load","error_count","uptime_hours","maintenance_cost"]:
            scale=max(float(X[c].std())*0.03,0.01)
            noise[c]=noise[c]+__import__("numpy").random.default_rng(42).normal(0,scale,len(noise))
        X_train=pd.concat([X_train,noise],ignore_index=True)
        y_train=pd.concat([y_train,pd.Series([1]*len(noise))],ignore_index=True)
    models={
      "Logistic Regression":Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler()),("model",LogisticRegression(max_iter=2000,class_weight="balanced"))]),
      "Random Forest":Pipeline([("imputer",SimpleImputer(strategy="median")),("model",RandomForestClassifier(n_estimators=300,max_depth=8,min_samples_leaf=2,random_state=42,class_weight="balanced"))])
    }
    results={}
    for name,model in models.items():
      model.fit(X_train,y_train); pred=model.predict(X_test); prob=model.predict_proba(X_test)[:,1]
      results[name]={"accuracy":round(float(accuracy_score(y_test,pred)),4),"precision":round(float(precision_score(y_test,pred,zero_division=0)),4),"recall":round(float(recall_score(y_test,pred,zero_division=0)),4),"f1":round(float(f1_score(y_test,pred,zero_division=0)),4),"roc_auc":round(float(roc_auc_score(y_test,prob)),4),"confusion_matrix":confusion_matrix(y_test,pred).tolist()}
    best=max(results,key=lambda k:(results[k]["f1"],results[k]["roc_auc"]))
    out=Path(__file__).resolve().parents[1]/"models"; out.mkdir(exist_ok=True)
    joblib.dump({"model":models[best],"features":FEATURE_COLUMNS,"model_name":best,"metrics":results,"target":"failure within next 30 days","training_rows":len(df),"leakage_safe":True},out/"failure_prediction_model.pkl")
    (out/"model_metrics.json").write_text(json.dumps({"selected_model":best,"metrics":results,"training_rows":len(df),"positive_rows":int(y.sum()),"negative_rows":int((y==0).sum())},indent=2))
    print(json.dumps({"selected_model":best,"metrics":results,"training_rows":len(df),"positive_rows":int(y.sum()),"negative_rows":int((y==0).sum())},indent=2))

if __name__=="__main__": main()
