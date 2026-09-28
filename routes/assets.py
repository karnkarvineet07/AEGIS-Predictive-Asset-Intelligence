from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import query
from routes.security import require_role
assets_bp=Blueprint("assets",__name__,url_prefix="/assets")

def guard():
    return "user_id" in session

@assets_bp.route("/")
def list_assets():
    if not guard(): return redirect(url_for("auth.login"))
    q=request.args.get("q",""); typ=request.args.get("type",""); status=request.args.get("status","")
    sql="""SELECT a.*,l.location_name,h.risk_level,h.failure_probability,h.health_score
           FROM assets a JOIN locations l USING(location_id)
           LEFT JOIN asset_health_view h USING(asset_id)
           WHERE (a.asset_name LIKE %s OR a.asset_code LIKE %s)"""
    params=[f"%{q}%",f"%{q}%"]
    if typ: sql+=" AND a.asset_type=%s"; params.append(typ)
    if status: sql+=" AND a.status=%s"; params.append(status)
    sql+=" ORDER BY a.asset_code ASC"
    return render_template("assets.html",assets=query(sql,params),q=q,typ=typ,status=status)

@assets_bp.route("/<int:asset_id>")
def detail(asset_id):
    if not guard(): return redirect(url_for("auth.login"))
    asset=query("""SELECT a.*,l.location_name,h.risk_level,h.failure_probability,h.health_score,h.prediction_date
                   FROM assets a JOIN locations l USING(location_id) LEFT JOIN asset_health_view h USING(asset_id)
                   WHERE a.asset_id=%s""",(asset_id,),"one")
    if not asset: return render_template("error.html",code=404,message="Asset not found."),404
    metrics=query("SELECT * FROM asset_metrics WHERE asset_id=%s ORDER BY recorded_at DESC LIMIT 12",(asset_id,))
    failures=query("SELECT * FROM failures WHERE asset_id=%s ORDER BY failure_date DESC",(asset_id,))
    maintenance=query("""SELECT m.*,t.technician_name FROM maintenance m LEFT JOIN technicians t USING(technician_id)
                         WHERE m.asset_id=%s ORDER BY maintenance_date DESC""",(asset_id,))
    predictions=query("SELECT * FROM predictions WHERE asset_id=%s ORDER BY prediction_date DESC,prediction_id DESC LIMIT 10",(asset_id,))
    return render_template("asset_detail.html",asset=asset,metrics=metrics,failures=failures,maintenance=maintenance,predictions=predictions)

@assets_bp.route("/add",methods=["POST"])
@require_role("MANAGER")
def add():
    f=request.form
    query("""INSERT INTO assets(asset_code,asset_name,asset_type,manufacturer,model,serial_number,purchase_date,installation_date,warranty_end_date,location_id,criticality)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
          (f["asset_code"],f["asset_name"],f["asset_type"],f.get("manufacturer"),f.get("model"),f.get("serial_number"),f.get("purchase_date") or None,f["installation_date"],f.get("warranty_end_date") or None,f["location_id"],f["criticality"]),commit=True)
    flash("Asset added successfully.","success"); return redirect(url_for("assets.list_assets"))

@assets_bp.route("/delete/<int:asset_id>",methods=["POST"])
@require_role("ADMIN")
def delete(asset_id):
    query("DELETE FROM assets WHERE asset_id=%s",(asset_id,),commit=True)
    flash("Asset removed.","success"); return redirect(url_for("assets.list_assets"))
