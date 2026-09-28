from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]

def test_model_artifact_exists_and_is_loadable():
    bundle = joblib.load(ROOT / "models" / "failure_prediction_model.pkl")
    assert bundle["leakage_safe"] is True
    assert len(bundle["features"]) == 13
    assert "model" in bundle

def test_training_sql_is_as_of_and_future_labeled():
    text = (ROOT / "ml" / "train_model.py").read_text()
    assert "f.failure_date < DATE(am.recorded_at)" in text
    assert "f2.failure_date > DATE(am.recorded_at)" in text
    assert "failure_within_30_days" in text

def test_security_controls_present():
    assert (ROOT / "routes" / "security.py").exists()
    auth = (ROOT / "routes" / "auth.py").read_text()
    assert "check_password_hash" in auth
    assert "generate_password_hash" in auth
    assert "role" in auth

def test_trigger_handles_insert_and_update_completion():
    text = (ROOT / "database" / "triggers.sql").read_text()
    assert "trg_maintenance_after_insert" in text
    assert "trg_maintenance_after_update" in text
    assert "NEW.maintenance_status='COMPLETED'" in text
