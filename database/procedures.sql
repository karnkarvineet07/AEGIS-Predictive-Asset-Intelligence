USE predictive_asset_maintenance;
DELIMITER //

DROP PROCEDURE IF EXISTS calculate_asset_health//
CREATE PROCEDURE calculate_asset_health(IN p_asset_id INT)
BEGIN
  SELECT asset_id, asset_code, asset_name,
    ROUND(100 - LEAST(100,
      COALESCE(AVG(temperature),0) * 0.35 +
      COALESCE(AVG(error_count),0) * 1.2 +
      COALESCE(AVG(cpu_usage),0) * 0.12
    ),2) AS health_indicator
  FROM assets a LEFT JOIN asset_metrics m USING(asset_id)
  WHERE a.asset_id=p_asset_id
  GROUP BY asset_id,asset_code,asset_name;
END//

DROP PROCEDURE IF EXISTS get_asset_maintenance_history//
CREATE PROCEDURE get_asset_maintenance_history(IN p_asset_id INT)
BEGIN
  SELECT m.maintenance_id,m.maintenance_date,m.maintenance_type,m.description,
         m.cost,m.downtime_hours,m.maintenance_status,t.technician_name
  FROM maintenance m LEFT JOIN technicians t USING(technician_id)
  WHERE m.asset_id=p_asset_id ORDER BY m.maintenance_date DESC;
END//

DROP PROCEDURE IF EXISTS get_high_risk_assets//
CREATE PROCEDURE get_high_risk_assets()
BEGIN
  SELECT * FROM high_risk_assets_view ORDER BY health_score ASC, failure_probability DESC;
END//

DROP PROCEDURE IF EXISTS calculate_maintenance_cost//
CREATE PROCEDURE calculate_maintenance_cost(IN p_asset_id INT)
BEGIN
  SELECT a.asset_id,a.asset_code,a.asset_name,COALESCE(SUM(m.cost),0) total_cost
  FROM assets a LEFT JOIN maintenance m USING(asset_id)
  WHERE a.asset_id=p_asset_id GROUP BY a.asset_id,a.asset_code,a.asset_name;
END//

DROP PROCEDURE IF EXISTS generate_asset_summary//
CREATE PROCEDURE generate_asset_summary(IN p_asset_id INT)
BEGIN
  SELECT a.asset_id,a.asset_code,a.asset_name,a.asset_type,a.criticality,a.status,
    l.location_name,
    (SELECT COUNT(*) FROM failures f WHERE f.asset_id=a.asset_id) failure_count,
    (SELECT COUNT(*) FROM maintenance m WHERE m.asset_id=a.asset_id) maintenance_count,
    (SELECT MAX(prediction_date) FROM predictions p WHERE p.asset_id=a.asset_id) last_prediction_date
  FROM assets a JOIN locations l USING(location_id)
  WHERE a.asset_id=p_asset_id;
END//
DELIMITER ;
