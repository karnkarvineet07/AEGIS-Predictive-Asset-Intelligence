from flask import Blueprint,render_template,session,redirect,url_for
from db import query
analytics_bp=Blueprint("analytics",__name__)
@analytics_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:return redirect(url_for("auth.login"))
    k=query("""SELECT
      (SELECT COUNT(*) FROM assets WHERE status<>'RETIRED') total_assets,
      (SELECT COUNT(*) FROM asset_health_view WHERE risk_level='LOW') healthy_assets,
      (SELECT COUNT(*) FROM asset_health_view WHERE risk_level IN ('MEDIUM','HIGH')) at_risk,
      (SELECT COUNT(*) FROM asset_health_view WHERE risk_level='HIGH') high_risk,
      (SELECT COUNT(*) FROM failures) total_failures,
      (SELECT COUNT(*) FROM maintenance_schedule WHERE status='PENDING' AND scheduled_date BETWEEN CURDATE() AND CURDATE()+INTERVAL 14 DAY) upcoming,
      (SELECT COALESCE(SUM(cost),0) FROM maintenance) maintenance_cost""")
    return render_template("dashboard.html",kpi=k,charts=chart_data(),alerts=alerts())

def chart_data():
    return {
      "types":query("SELECT asset_type label,COUNT(*) value FROM assets GROUP BY asset_type"),
      "risk":query("SELECT risk_level label,COUNT(*) value FROM asset_health_view GROUP BY risk_level"),
      "failures":query("""SELECT DATE_FORMAT(failure_date,'%Y-%m') label,COUNT(*) value FROM failures
                          GROUP BY label ORDER BY label"""),
      "cost":query("""SELECT DATE_FORMAT(maintenance_date,'%Y-%m') label,ROUND(SUM(cost),2) value FROM maintenance
                      GROUP BY label ORDER BY label"""),
      "failure_types":query("SELECT a.asset_type label,COUNT(f.failure_id) value FROM assets a LEFT JOIN failures f USING(asset_id) GROUP BY a.asset_type"),
      "severity":query("SELECT severity label,COUNT(*) value FROM failures GROUP BY severity"),
      "status":query("SELECT status label,COUNT(*) value FROM assets GROUP BY status"),
      "maint_types":query("SELECT maintenance_type label,COUNT(*) value FROM maintenance GROUP BY maintenance_type")
    }
def alerts():
    return {
      "high":query("""SELECT asset_id,asset_code,asset_name,risk_level,health_score FROM asset_health_view
                      WHERE risk_level='HIGH' ORDER BY health_score LIMIT 8"""),
      "temp":query("""SELECT a.asset_code,a.asset_name,m.temperature,m.error_count FROM assets a JOIN asset_metrics m USING(asset_id)
                      WHERE m.recorded_at=(SELECT MAX(x.recorded_at) FROM asset_metrics x WHERE x.asset_id=m.asset_id)
                      AND (m.temperature>=70 OR m.error_count>=20) ORDER BY m.temperature DESC LIMIT 8"""),
      "maintenance":query("""SELECT s.*,a.asset_code,a.asset_name FROM maintenance_schedule s JOIN assets a USING(asset_id)
                             WHERE s.status='PENDING' ORDER BY s.scheduled_date LIMIT 8""")
    }
