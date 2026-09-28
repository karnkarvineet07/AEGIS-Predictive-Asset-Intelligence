from functools import wraps
from secrets import token_urlsafe
from flask import session, request, redirect, url_for, flash, jsonify

ROLE_ORDER = {"VIEWER": 0, "TECHNICIAN": 1, "MANAGER": 2, "ADMIN": 3}

def logged_in():
    return "user_id" in session

def role_at_least(role):
    return ROLE_ORDER.get(session.get("role", ""), -1) >= ROLE_ORDER.get(role, 99)

def require_role(min_role="VIEWER"):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not logged_in():
                return redirect(url_for("auth.login"))
            if not role_at_least(min_role):
                flash("You do not have permission for this action.", "danger")
                return redirect(request.referrer or url_for("analytics.dashboard"))
            return fn(*args, **kwargs)
        return wrapped
    return deco

def api_require_role(min_role="VIEWER"):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not logged_in(): return jsonify(error="Unauthorized"), 401
            if not role_at_least(min_role): return jsonify(error="Forbidden"), 403
            return fn(*args, **kwargs)
        return wrapped
    return deco

def ensure_csrf_token():
    token=session.get("csrf_token")
    if not token:
        token=token_urlsafe(32); session["csrf_token"]=token
    return token

def validate_csrf():
    supplied=request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    expected=session.get("csrf_token")
    return bool(expected and supplied and supplied == expected)
