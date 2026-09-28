USE predictive_asset_maintenance;
DELIMITER //

DROP TRIGGER IF EXISTS trg_failure_after_insert//
CREATE TRIGGER trg_failure_after_insert
AFTER INSERT ON failures
FOR EACH ROW
BEGIN
  UPDATE assets SET status='FAILED' WHERE asset_id=NEW.asset_id;
  IF NEW.severity IN ('HIGH','CRITICAL') THEN
    INSERT INTO maintenance_schedule(asset_id,scheduled_date,priority,reason)
    SELECT NEW.asset_id,DATE_ADD(NEW.failure_date,INTERVAL 1 DAY),NEW.severity,
           CONCAT('Follow-up required after ',NEW.severity,' severity failure: ',NEW.failure_type)
    WHERE NOT EXISTS (SELECT 1 FROM maintenance_schedule s
                      WHERE s.asset_id=NEW.asset_id AND s.status='PENDING'
                        AND s.reason LIKE CONCAT('Follow-up required after ',NEW.severity,'%'));
  END IF;
END//

DROP TRIGGER IF EXISTS trg_maintenance_after_insert//
CREATE TRIGGER trg_maintenance_after_insert
AFTER INSERT ON maintenance
FOR EACH ROW
BEGIN
  IF NEW.maintenance_status='IN_PROGRESS' THEN
    UPDATE assets SET status='MAINTENANCE' WHERE asset_id=NEW.asset_id;
  ELSEIF NEW.maintenance_status='COMPLETED' THEN
    UPDATE assets SET status='ACTIVE' WHERE asset_id=NEW.asset_id AND status IN ('MAINTENANCE','FAILED');
  END IF;
END//

DROP TRIGGER IF EXISTS trg_maintenance_after_update//
CREATE TRIGGER trg_maintenance_after_update
AFTER UPDATE ON maintenance
FOR EACH ROW
BEGIN
  IF NEW.maintenance_status='IN_PROGRESS' AND OLD.maintenance_status<>'IN_PROGRESS' THEN
    UPDATE assets SET status='MAINTENANCE' WHERE asset_id=NEW.asset_id;
  ELSEIF NEW.maintenance_status='COMPLETED' AND OLD.maintenance_status<>'COMPLETED' THEN
    UPDATE assets SET status='ACTIVE' WHERE asset_id=NEW.asset_id AND status IN ('MAINTENANCE','FAILED');
    UPDATE maintenance_schedule SET status='COMPLETED'
      WHERE asset_id=NEW.asset_id AND status='PENDING' AND scheduled_date<=NEW.maintenance_date;
  END IF;
END//

DELIMITER ;
