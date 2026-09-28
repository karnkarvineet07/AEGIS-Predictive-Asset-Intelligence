from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query
from routes.security import require_role

admin_data_bp = Blueprint("admin_data", __name__)

def logged_in():
    return "user_id" in session

@admin_data_bp.route("/technicians")
def technicians():
    if not logged_in(): return redirect(url_for("auth.login"))
    return render_template("technicians.html", rows=query("SELECT * FROM technicians ORDER BY technician_name"))

@admin_data_bp.route("/technicians/add", methods=["POST"])
@require_role("ADMIN")
def add_technician():
    f=request.form
    query("""INSERT INTO technicians(technician_name,email,specialization,phone,status)
             VALUES(%s,%s,%s,%s,%s)""",
          (f["technician_name"],f.get("email") or None,f.get("specialization"),f.get("phone"),f.get("status","ACTIVE")),commit=True)
    flash("Technician added.","success")
    return redirect(url_for("admin_data.technicians"))

@admin_data_bp.route("/locations")
def locations():
    if not logged_in(): return redirect(url_for("auth.login"))
    return render_template("locations.html", rows=query("SELECT * FROM locations ORDER BY city,location_name"))

@admin_data_bp.route("/locations/add", methods=["POST"])
@require_role("ADMIN")
def add_location():
    f=request.form
    query("""INSERT INTO locations(location_name,building,floor,city,region)
             VALUES(%s,%s,%s,%s,%s)""",
          (f["location_name"],f["building"],f.get("floor"),f["city"],f.get("region")),commit=True)
    flash("Location added.","success")
    return redirect(url_for("admin_data.locations"))

@admin_data_bp.route("/reports")
def reports():
    if not logged_in(): return redirect(url_for("auth.login"))
    return render_template("reports.html",
        summary=query("SELECT * FROM asset_failure_summary ORDER BY total_repair_cost DESC LIMIT 20"),
        high_risk=query("SELECT * FROM high_risk_assets_view ORDER BY health_score ASC LIMIT 20"),
        maint=query("SELECT * FROM maintenance_summary ORDER BY total_maintenance_cost DESC LIMIT 20"))
