from flask import Flask, redirect, url_for, request, session, jsonify
from config import Config
from routes.auth import auth_bp
from routes.assets import assets_bp
from routes.maintenance import maintenance_bp
from routes.failures import failures_bp
from routes.predictions import predictions_bp
from routes.analytics import analytics_bp
from routes.api import api_bp
from routes.admin_data import admin_data_bp
from db import init_db
from routes.security import ensure_csrf_token, validate_csrf

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.jinja_env.globals["csrf_token"] = ensure_csrf_token

    @app.before_request
    def csrf_protect():
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and session.get("user_id"):
            if not validate_csrf():
                if request.path.startswith("/api/"):
                    return jsonify(error="Invalid or missing CSRF token"), 400
                return "Invalid or missing CSRF token", 400
    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(failures_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_data_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="The requested page was not found."), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500

    return app

from flask import render_template
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
