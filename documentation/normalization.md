# Database Normalization

## 1NF
All attributes are atomic and repeating groups are removed. For example, an asset does not store multiple maintenance events in a comma-separated field; each event is a row in `maintenance`.

## 2NF
All non-key attributes depend on the whole primary key. The transactional tables use surrogate primary keys (`maintenance_id`, `failure_id`, `metric_id`, etc.), so descriptive fields depend on their row identifier rather than on only part of a composite key.

## 3NF
Transitive dependencies are separated. Technician details live in `technicians`, location details in `locations`, and asset details in `assets`. Maintenance stores only `technician_id` and `asset_id`, not repeated technician/location descriptions.

### Example decomposition
Unnormalized record:
`AssetCode, AssetName, LocationName, TechnicianName, MaintenanceDate, MaintenanceCost, FailureType`

Decomposed into:
- `assets(asset_id, asset_code, asset_name, location_id, ...)`
- `locations(location_id, location_name, ...)`
- `technicians(technician_id, technician_name, ...)`
- `maintenance(maintenance_id, asset_id, technician_id, maintenance_date, cost, ...)`
- `failures(failure_id, asset_id, failure_date, failure_type, ...)`

This reduces redundancy, prevents update anomalies, and preserves referential integrity.
