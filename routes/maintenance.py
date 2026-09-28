from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from db import query
from routes.security import require_role
maintenance_bp=Blueprint("maintenance",__name__,url_prefix="/maintenance")
@maintenance_bp.route("/")
def index():
    if "user_id" not in session:return redirect(url_for("auth.login"))
    rows=query("""SELECT m.*,a.asset_code,a.asset_name,t.technician_name FROM maintenance m
                  JOIN assets a USING(asset_id) LEFT JOIN technicians t USING(technician_id)
                  ORDER BY m.maintenance_date DESC""")
    return render_template("maintenance.html",rows=rows)
@maintenance_bp.route("/add",methods=["POST"])
@require_role("TECHNICIAN")
def add():
    f=request.form
    query("""INSERT INTO maintenance(asset_id,technician_id,maintenance_date,maintenance_type,description,cost,downtime_hours,maintenance_status)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",(f["asset_id"],f.get("technician_id") or None,f["maintenance_date"],f["maintenance_type"],f.get("description"),f.get("cost",0),f.get("downtime_hours",0),f["maintenance_status"]),commit=True)
    flash("Maintenance record added.","success");return redirect(url_for("maintenance.index"))
