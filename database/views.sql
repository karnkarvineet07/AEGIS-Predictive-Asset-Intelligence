USE predictive_asset_maintenance;

CREATE OR REPLACE VIEW asset_failure_summary AS
SELECT a.asset_id,a.asset_code,a.asset_name,a.asset_type,a.criticality,a.status,
       COUNT(f.failure_id) failure_count,
       COALESCE(SUM(f.downtime_hours),0) total_downtime_hours,
       COALESCE(SUM(f.repair_cost),0) total_repair_cost,
       MAX(f.failure_date) last_failure_date
FROM assets a LEFT JOIN failures f ON a.asset_id=f.asset_id
GROUP BY a.asset_id,a.asset_code,a.asset_name,a.asset_type,a.criticality,a.status;

CREATE OR REPLACE VIEW maintenance_summary AS
SELECT a.asset_id,a.asset_code,a.asset_name,
       COUNT(m.maintenance_id) maintenance_count,
       COALESCE(SUM(m.cost),0) total_maintenance_cost,
       MAX(m.maintenance_date) last_maintenance_date
FROM assets a LEFT JOIN maintenance m ON a.asset_id=m.asset_id
GROUP BY a.asset_id,a.asset_code,a.asset_name;

CREATE OR REPLACE VIEW asset_health_view AS
SELECT a.asset_id,a.asset_code,a.asset_name,a.asset_type,a.criticality,a.status,
       COALESCE(p.failure_probability,0) failure_probability,
       COALESCE(p.risk_level,'LOW') risk_level,
       COALESCE(p.health_score,100) health_score,
       p.prediction_date
FROM assets a
LEFT JOIN predictions p ON p.prediction_id=(
  SELECT p2.prediction_id FROM predictions p2
  WHERE p2.asset_id=a.asset_id ORDER BY p2.prediction_date DESC,p2.prediction_id DESC LIMIT 1
);

CREATE OR REPLACE VIEW high_risk_assets_view AS
SELECT * FROM asset_health_view WHERE risk_level='HIGH' OR health_score < 50;
