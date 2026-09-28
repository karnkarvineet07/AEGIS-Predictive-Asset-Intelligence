USE predictive_asset_maintenance;

-- 1 INNER JOIN: assets and locations
SELECT a.asset_code,a.asset_name,l.location_name FROM assets a INNER JOIN locations l ON a.location_id=l.location_id;

-- 2 LEFT JOIN: include assets with no failures
SELECT a.asset_code,COUNT(f.failure_id) failure_count FROM assets a LEFT JOIN failures f USING(asset_id) GROUP BY a.asset_id;

-- 3 RIGHT JOIN: technicians and maintenance
SELECT t.technician_name,m.maintenance_id FROM maintenance m RIGHT JOIN technicians t USING(technician_id);

-- 4 GROUP BY: assets by type
SELECT asset_type,COUNT(*) total_assets FROM assets GROUP BY asset_type;

-- 5 HAVING: asset types with at least 5 assets
SELECT asset_type,COUNT(*) total_assets FROM assets GROUP BY asset_type HAVING COUNT(*)>=5;

-- 6 Aggregate: repair cost
SELECT SUM(repair_cost) total_repair_cost,AVG(repair_cost) avg_repair_cost FROM failures;

-- 7 Subquery: assets above average failure count
SELECT * FROM asset_failure_summary WHERE failure_count>(SELECT AVG(failure_count) FROM asset_failure_summary);

-- 8 Correlated subquery: latest metric per asset
SELECT a.asset_code,m.recorded_at,m.temperature FROM assets a JOIN asset_metrics m ON a.asset_id=m.asset_id
WHERE m.recorded_at=(SELECT MAX(m2.recorded_at) FROM asset_metrics m2 WHERE m2.asset_id=m.asset_id);

-- 9 CASE: risk category from probability
SELECT asset_id,failure_probability,
CASE WHEN failure_probability>=.70 THEN 'HIGH' WHEN failure_probability>=.40 THEN 'MEDIUM' ELSE 'LOW' END risk
FROM predictions;

-- 10 CTE: recent failures
WITH recent AS (SELECT * FROM failures WHERE failure_date>=CURDATE()-INTERVAL 90 DAY)
SELECT asset_id,COUNT(*) failures FROM recent GROUP BY asset_id;

-- 11 Window function: rank assets by repair cost
SELECT asset_id,asset_code,total_repair_cost,
RANK() OVER(ORDER BY total_repair_cost DESC) cost_rank FROM asset_failure_summary;

-- 12 Running total of maintenance cost by date
SELECT maintenance_date,SUM(cost) daily_cost,
SUM(SUM(cost)) OVER(ORDER BY maintenance_date) running_cost FROM maintenance GROUP BY maintenance_date;

-- 13 Date function: maintenance age
SELECT asset_id,DATEDIFF(CURDATE(),MAX(maintenance_date)) days_since_maintenance
FROM maintenance GROUP BY asset_id;

-- 14 Conditional aggregation: severity counts
SELECT asset_id,
SUM(severity='CRITICAL') critical_failures,
SUM(severity='HIGH') high_failures,
SUM(severity='MEDIUM') medium_failures
FROM failures GROUP BY asset_id;

-- 15 Top 10 high-risk assets
SELECT * FROM high_risk_assets_view ORDER BY failure_probability DESC LIMIT 10;

-- 16 Maintenance type cost
SELECT maintenance_type,SUM(cost) total_cost,AVG(cost) avg_cost FROM maintenance GROUP BY maintenance_type;

-- 17 Failure trend by month
SELECT DATE_FORMAT(failure_date,'%Y-%m') month,COUNT(*) failures FROM failures GROUP BY month ORDER BY month;

-- 18 Assets with no maintenance
SELECT a.asset_code,a.asset_name FROM assets a WHERE NOT EXISTS(SELECT 1 FROM maintenance m WHERE m.asset_id=a.asset_id);

-- 19 Latest prediction using window function
WITH ranked AS (
 SELECT p.*,ROW_NUMBER() OVER(PARTITION BY asset_id ORDER BY prediction_date DESC,prediction_id DESC) rn FROM predictions p
) SELECT * FROM ranked WHERE rn=1;

-- 20 Failure rate by asset type
SELECT a.asset_type,COUNT(DISTINCT f.failure_id) failures,COUNT(DISTINCT a.asset_id) assets,
ROUND(COUNT(DISTINCT f.failure_id)/NULLIF(COUNT(DISTINCT a.asset_id),0),2) failures_per_asset
FROM assets a LEFT JOIN failures f USING(asset_id) GROUP BY a.asset_type ORDER BY failures_per_asset DESC;
