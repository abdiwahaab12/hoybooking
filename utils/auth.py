from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from flask import flash, g, redirect, session, url_for

TFunc = TypeVar("TFunc", bound=Callable[..., Any])


def get_current_user():
    """
    Loads the currently logged-in user from the DB using session['user_id'].
    Cached on flask.g for the request lifetime.
    """
    if hasattr(g, "current_user"):
        return g.current_user

    user_id = session.get("user_id")
    if not user_id:
        g.current_user = None
        return None

    from models.user import User  # local import to avoid circular imports

    g.current_user = User.query.get(user_id)
    return g.current_user


def login_required(view_func: TFunc) -> TFunc:
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def admin_required(view_func: TFunc) -> TFunc:
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id") or session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.admin_login", next=url_for("admin.admin_dashboard")))
        return view_func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]

