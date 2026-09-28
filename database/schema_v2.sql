CREATE DATABASE IF NOT EXISTS predictive_asset_maintenance_v2
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE predictive_asset_maintenance_v2;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ADMIN','MANAGER','TECHNICIAN','VIEWER') NOT NULL DEFAULT 'VIEWER',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
  location_id INT AUTO_INCREMENT PRIMARY KEY,
  location_name VARCHAR(100) NOT NULL UNIQUE,
  building VARCHAR(100) NOT NULL,
  floor VARCHAR(30),
  city VARCHAR(80) NOT NULL,
  region VARCHAR(80),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS technicians (
  technician_id INT AUTO_INCREMENT PRIMARY KEY,
  technician_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  specialization VARCHAR(100),
  phone VARCHAR(30),
  status ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS assets (
  asset_id INT AUTO_INCREMENT PRIMARY KEY,
  asset_code VARCHAR(30) NOT NULL UNIQUE,
  asset_name VARCHAR(120) NOT NULL,
  asset_type ENUM('SERVER','ROUTER','SWITCH','FIREWALL','STORAGE','WORKSTATION','PRINTER') NOT NULL,
  manufacturer VARCHAR(80),
  model VARCHAR(100),
  serial_number VARCHAR(100) UNIQUE,
  purchase_date DATE,
  installation_date DATE NOT NULL,
  warranty_end_date DATE,
  location_id INT NOT NULL,
  criticality ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL DEFAULT 'MEDIUM',
  status ENUM('ACTIVE','MAINTENANCE','FAILED','RETIRED') NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_asset_location FOREIGN KEY(location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS maintenance (
  maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  technician_id INT,
  maintenance_date DATE NOT NULL,
  maintenance_type ENUM('PREVENTIVE','CORRECTIVE','EMERGENCY','PREDICTIVE') NOT NULL,
  description VARCHAR(500),
  cost DECIMAL(12,2) NOT NULL DEFAULT 0,
  downtime_hours DECIMAL(8,2) NOT NULL DEFAULT 0,
  maintenance_status ENUM('SCHEDULED','IN_PROGRESS','COMPLETED','CANCELLED') NOT NULL DEFAULT 'SCHEDULED',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_maint_asset FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  CONSTRAINT fk_maint_tech FOREIGN KEY(technician_id) REFERENCES technicians(technician_id) ON DELETE SET NULL,
  CONSTRAINT chk_maint_cost CHECK(cost >= 0),
  CONSTRAINT chk_maint_downtime CHECK(downtime_hours >= 0)
);

CREATE TABLE IF NOT EXISTS asset_metrics (
  metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  recorded_at DATETIME NOT NULL,
  cpu_usage DECIMAL(5,2) NOT NULL DEFAULT 0,
  memory_usage DECIMAL(5,2) NOT NULL DEFAULT 0,
  disk_usage DECIMAL(5,2) NOT NULL DEFAULT 0,
  temperature DECIMAL(6,2) NOT NULL DEFAULT 0,
  network_load DECIMAL(6,2) NOT NULL DEFAULT 0,
  error_count INT NOT NULL DEFAULT 0,
  uptime_hours DECIMAL(10,2) NOT NULL DEFAULT 0,
  power_consumption DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_metric_asset FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  CONSTRAINT chk_metric_pct CHECK(cpu_usage BETWEEN 0 AND 100 AND memory_usage BETWEEN 0 AND 100 AND disk_usage BETWEEN 0 AND 100),
  INDEX idx_metrics_asset_time(asset_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS failures (
  failure_id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  failure_date DATE NOT NULL,
  failure_type VARCHAR(100) NOT NULL,
  severity ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
  downtime_hours DECIMAL(8,2) NOT NULL DEFAULT 0,
  root_cause VARCHAR(300),
  resolution VARCHAR(500),
  repair_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_failure_asset FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  INDEX idx_failure_date(failure_date),
  INDEX idx_failure_asset(asset_id)
);

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  prediction_date DATE NOT NULL,
  failure_probability DECIMAL(6,5) NOT NULL,
  risk_level ENUM('LOW','MEDIUM','HIGH') NOT NULL,
  health_score DECIMAL(5,2) NOT NULL,
  recommendation VARCHAR(500) NOT NULL,
  model_version VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prediction_asset FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  INDEX idx_prediction_risk(risk_level),
  INDEX idx_prediction_date(prediction_date)
);

CREATE TABLE IF NOT EXISTS maintenance_schedule (
  schedule_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  scheduled_date DATE NOT NULL,
  priority ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
  reason VARCHAR(500) NOT NULL,
  status ENUM('PENDING','COMPLETED','CANCELLED') NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_schedule_asset FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  INDEX idx_schedule_date(scheduled_date)
);

CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_criticality ON assets(criticality);
CREATE INDEX idx_maintenance_date ON maintenance(maintenance_date);
CREATE INDEX idx_maintenance_asset_date ON maintenance(asset_id, maintenance_date);
