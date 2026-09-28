from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from db import query
from routes.security import require_role
failures_bp=Blueprint("failures",__name__,url_prefix="/failures")
@failures_bp.route("/")
def index():
    if "user_id" not in session:return redirect(url_for("auth.login"))
    rows=query("""SELECT f.*,a.asset_code,a.asset_name FROM failures f JOIN assets a USING(asset_id)
                  ORDER BY f.failure_date DESC""")
    return render_template("failures.html",rows=rows)
@failures_bp.route("/add",methods=["POST"])
@require_role("TECHNICIAN")
def add():
    f=request.form
    query("""INSERT INTO failures(asset_id,failure_date,failure_type,severity,downtime_hours,root_cause,resolution,repair_cost)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",(f["asset_id"],f["failure_date"],f["failure_type"],f["severity"],f.get("downtime_hours",0),f.get("root_cause"),f.get("resolution"),f.get("repair_cost",0)),commit=True)
    flash("Failure recorded; database trigger applied automatically.","success");return redirect(url_for("failures.index"))
