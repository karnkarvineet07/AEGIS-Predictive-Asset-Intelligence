def classify_risk(p):
    return "HIGH" if p >= .70 else ("MEDIUM" if p >= .40 else "LOW")

def test_risk_low(): assert classify_risk(.20)=="LOW"
def test_risk_medium(): assert classify_risk(.50)=="MEDIUM"
def test_risk_high(): assert classify_risk(.82)=="HIGH"

def test_health_score_range():
    p=.82
    score=max(0,min(100,round(100-p*60)))
    assert 0 <= score <= 100
