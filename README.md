# Predictive AI Asset Maintenance System

A professional local-first DBMS laboratory project for IT infrastructure predictive maintenance.

## What it demonstrates
- MySQL 8+ relational design and 3NF normalization
- Primary/foreign keys, constraints and indexes
- Views, stored procedures and triggers
- Advanced SQL: joins, subqueries, CTEs, windows, ranking and conditional aggregation
- Flask REST/API layer
- Synthetic but patterned telemetry/failure/maintenance data
- Logistic Regression vs Random Forest
- Failure probability, risk classification and health score
- Enterprise-style dashboard

## Tech stack
Python 3.11+ · Flask · MySQL 8+ · Pandas · NumPy · Scikit-learn · Joblib · Bootstrap · Chart.js

## Installation
### 1. Install MySQL
Create a local MySQL 8+ server.

### 2. Create database/tables
Run in MySQL Workbench or the mysql client:
```sql
SOURCE database/schema.sql;
SOURCE database/views.sql;
SOURCE database/procedures.sql;
SOURCE database/triggers.sql;
SOURCE database/seed.sql;
```
Run the scripts in that order. If your MySQL client does not preserve `DELIMITER` in the chosen interface, run procedures/triggers in Workbench or another SQL client that supports it.

### 3. Python environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure
Copy `.env.example` to `.env` and set your local MySQL password.

### 5. Train the model
```bash
python -m ml.train_model
```
This compares Logistic Regression and Random Forest and writes `models/failure_prediction_model.pkl`.

### 6. Run
```bash
python app.py
```
Open `http://127.0.0.1:5000`.

## Demo credentials
Email: `admin@demo.local`  
Password: `Admin@123`

These credentials are for the synthetic academic seed database only.

## API
- GET `/api/assets`
- POST `/api/assets`
- GET `/api/assets/<asset_id>`
- PUT `/api/assets/<asset_id>`
- DELETE `/api/assets/<asset_id>`
- GET `/api/predictions`
- GET `/api/high-risk-assets`
- GET `/api/analytics`
- POST `/api/predict/<asset_id>`

Login first because API routes use the same Flask session.

## Project structure
See the repository tree for database, ML, routes, templates, diagrams, documentation, presentation and tests.

## Important academic note
The synthetic data is deliberately patterned so that older assets, abnormal telemetry, prior failures and long maintenance gaps are generally associated with greater risk. The resulting model is for academic demonstration, not production reliability certification.

## Security
- DB password is supplied through `.env`.
- SQL uses parameterized queries in Flask.
- Passwords are stored using Werkzeug-compatible PBKDF2 password hashing. Legacy SHA-256 hashes are accepted only for backward compatibility and upgraded after a successful login.
- Never commit `.env`.

## UI pages
Dashboard · Assets · Asset Detail · Maintenance · Failures · Predictions · Analytics · Technicians · Locations · Reports

## Team
Student 1: Vinit Karnkar  
Student 2: Project Partner


## Security and ML integrity notes
- Passwords use Werkzeug PBKDF2-style password hashing; legacy SHA-256 demo hashes are transparently upgraded after successful login.
- State-changing requests require a CSRF token. API state-changing requests accept the token through `X-CSRF-Token`.
- Roles are enforced: VIEWER (read), TECHNICIAN (maintenance/failure/prediction), MANAGER (asset creation/update), ADMIN (administration and deletion).
- ML training uses historical telemetry snapshots. Features only use information available at or before each snapshot; the target is failure during the following 30 days. This avoids target leakage.
- Run `python -m ml.train_model` after importing MySQL data to retrain. A validated model artifact is included in `models/`.
- Health score is an ML-derived 0-100 operational indicator; failure probability/risk and the health score are separate concepts from the database's raw telemetry indicators.
