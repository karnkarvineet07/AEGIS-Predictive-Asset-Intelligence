from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import query
from routes.security import ensure_csrf_token
import hashlib

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        user=query("SELECT * FROM users WHERE email=%s",(email,),fetch="one")
        valid=False; legacy=False
        if user:
            stored=user.get("password_hash","")
            try: valid=check_password_hash(stored,password)
            except (ValueError,TypeError): valid=False
            if not valid and len(stored)==64 and stored==hashlib.sha256(password.encode()).hexdigest():
                valid=True; legacy=True
        if valid:
            if legacy:
                query("UPDATE users SET password_hash=%s WHERE user_id=%s",(generate_password_hash(password),user["user_id"]),commit=True)
            session.clear()
            session["user_id"]=user["user_id"]; session["user_name"]=user["full_name"]; session["role"]=user["role"]; ensure_csrf_token()
            return redirect(url_for("analytics.dashboard"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear(); return redirect(url_for("auth.login"))
