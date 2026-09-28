# Database Documentation

## Core tables
`users`, `locations`, `technicians`, `assets`, `maintenance`, `asset_metrics`, `failures`, `predictions`, `maintenance_schedule`.

## Important DBMS features
- Primary and foreign keys preserve identity and referential integrity.
- CHECK constraints validate non-negative cost/downtime and metric ranges.
- UNIQUE constraints protect asset codes, serial numbers, location names and emails.
- Indexes improve lookups for asset types, status, dates, and time-series metrics.
- Views expose reusable analytical datasets.
- Stored procedures encapsulate common asset-health and maintenance queries.
- Triggers synchronize asset status and create follow-up maintenance schedules.
- Advanced SQL demonstrates joins, grouping, subqueries, CTEs, windows, date functions, CASE, ranking and conditional aggregation.

## Transaction/ACID relevance
The Flask database helper commits successful writes and rolls back failed transactions. MySQL InnoDB provides atomicity, consistency, isolation and durability for transactional tables.

## ML-to-DB flow
1. Historical metrics/failures/maintenance are stored in MySQL.
2. `train_model.py` reads engineered features from SQL.
3. The selected model is persisted with Joblib.
4. `predict.py` retrieves current asset features and creates a prediction.
5. The prediction is written to `predictions`.
6. Dashboard views consume the latest prediction and present risk.
