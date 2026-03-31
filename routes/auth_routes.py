from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.extensions import bcrypt
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    next_url = request.args.get("next") or ""
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth.register", next=next_url))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return redirect(url_for("auth.register", next=next_url))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email is already registered. Please login.", "warning")
            return redirect(url_for("auth.login", next=next_url))

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        # Public registration is customer-only.
        user = User(name=name, email=email, password=hashed, role="customer")
        # Note: db commit is handled via SQLAlchemy session on request teardown.
        # We'll commit immediately for correctness.
        from models.extensions import db

        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login", next=next_url))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next") or ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        from models.extensions import db  # keep imports local to avoid cycles in early startup

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))
        if user.role != "customer":
            flash("Please use the admin login page for admin accounts.", "warning")
            return redirect(url_for("auth.admin_login"))

        session["user_id"] = user.id
        session["role"] = user.role

        # If the user came from a booking confirmation/payment step, honor `next`.
        if next_url and next_url.startswith("/"):
            return redirect(next_url)

        return redirect(url_for("admin.admin_dashboard") if user.role == "admin" else url_for("booking.customer_dashboard"))

    return render_template("login.html")


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    next_url = request.args.get("next") or request.form.get("next") or ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.admin_login", next=next_url))
        if user.role != "admin":
            flash("This account is not an admin account.", "warning")
            return redirect(url_for("auth.admin_login", next=next_url))

        session["user_id"] = user.id
        session["role"] = user.role

        if next_url and next_url.startswith("/"):
            return redirect(next_url)
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin_login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("public.home"))

