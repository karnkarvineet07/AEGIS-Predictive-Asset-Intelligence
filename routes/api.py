from flask import Blueprint,jsonify,request,session
from db import query
from ml.predict import predict_asset
from routes.security import api_require_role
api_bp=Blueprint("api",__name__,url_prefix="/api")
def auth():
    return "user_id" in session
@api_bp.get("/assets")
def assets():
    if not auth(): return jsonify(error="Unauthorized"),401
    return jsonify(query("SELECT * FROM assets ORDER BY asset_id DESC"))
@api_bp.post("/assets")
@api_require_role("MANAGER")
def create_asset():
    d=request.get_json(silent=True) or {}
    required=["asset_code","asset_name","asset_type","installation_date","location_id","criticality"]
    if any(not d.get(x) for x in required): return jsonify(error="Missing required fields"),400
    query("""INSERT INTO assets(asset_code,asset_name,asset_type,manufacturer,model,serial_number,installation_date,location_id,criticality)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
          tuple(d.get(x) for x in ["asset_code","asset_name","asset_type","manufacturer","model","serial_number","installation_date","location_id","criticality"]),commit=True)
    return jsonify(message="Asset created"),201
@api_bp.get("/assets/<int:asset_id>")
def asset(asset_id):
    if not auth(): return jsonify(error="Unauthorized"),401
    row=query("SELECT * FROM assets WHERE asset_id=%s",(asset_id,),"one")
    return jsonify(row or {"error":"Asset not found"}),200 if row else 404

@api_bp.put("/assets/<int:asset_id>")
@api_require_role("MANAGER")
def update_asset(asset_id):
    d=request.get_json(silent=True) or {}
    allowed=["asset_name","asset_type","manufacturer","model","serial_number","installation_date","location_id","criticality","status"]
    fields=[x for x in allowed if x in d]
    if not fields: return jsonify(error="No editable fields supplied"),400
    sql="UPDATE assets SET "+",".join(f"{x}=%s" for x in fields)+" WHERE asset_id=%s"
    query(sql,tuple(d[x] for x in fields)+(asset_id,),commit=True)
    return jsonify(message="Asset updated")

@api_bp.delete("/assets/<int:asset_id>")
@api_require_role("ADMIN")
def delete_asset(asset_id):
    query("DELETE FROM assets WHERE asset_id=%s",(asset_id,),commit=True); return jsonify(message="Deleted")
@api_bp.get("/predictions")
def predictions():
    if not auth(): return jsonify(error="Unauthorized"),401
    return jsonify(query("""SELECT p.*,a.asset_code,a.asset_name FROM predictions p JOIN assets a USING(asset_id)
                            ORDER BY p.prediction_date DESC,p.prediction_id DESC"""))
@api_bp.get("/high-risk-assets")
def high_risk():
    if not auth(): return jsonify(error="Unauthorized"),401
    return jsonify(query("SELECT * FROM high_risk_assets_view ORDER BY health_score"))
@api_bp.get("/analytics")
def analytics():
    if not auth(): return jsonify(error="Unauthorized"),401
    return jsonify({
      "assets_by_type":query("SELECT asset_type,COUNT(*) total FROM assets GROUP BY asset_type"),
      "risk":query("SELECT risk_level,COUNT(*) total FROM asset_health_view GROUP BY risk_level"),
      "failures":query("SELECT COUNT(*) total FROM failures")
    })
@api_bp.post("/predict/<int:asset_id>")
@api_require_role("TECHNICIAN")
def api_predict(asset_id):
    try:return jsonify(predict_asset(asset_id))
    except Exception as e:return jsonify(error=str(e)),400
