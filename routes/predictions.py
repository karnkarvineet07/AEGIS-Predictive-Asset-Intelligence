from flask import Blueprint,render_template,request,redirect,url_for,session,flash,jsonify
from db import query
from routes.security import require_role
from ml.predict import predict_asset
predictions_bp=Blueprint("predictions",__name__,url_prefix="/predictions")
@predictions_bp.route("/")
def index():
    if "user_id" not in session:return redirect(url_for("auth.login"))
    rows=query("""SELECT p.*,a.asset_code,a.asset_name,a.criticality FROM predictions p JOIN assets a USING(asset_id)
                  ORDER BY p.prediction_date DESC,p.prediction_id DESC""")
    return render_template("predictions.html",rows=rows)
@predictions_bp.route("/predict/<int:asset_id>",methods=["POST"])
@require_role("TECHNICIAN")
def predict(asset_id):
    try:
        result=predict_asset(asset_id)
        flash(f"Prediction generated: {result['risk']} risk ({result['probability']:.1%}).","success")
    except Exception as e:
        flash(str(e),"danger")
    return redirect(url_for("assets.detail",asset_id=asset_id))
