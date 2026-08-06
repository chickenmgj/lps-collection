from functools import wraps

from flask import flash, redirect, session


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "You must log in to access this page.",
                "login"
            )
            return redirect("/login")

        return function(*args, **kwargs)

    return decorated_function


def user_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "You must log in to access this page.",
                "login"
            )
            return redirect("/login")

        if session.get("user_role") != "user":
            flash(
                "This section is only available for user accounts."
            )
            return redirect("/")

        return function(*args, **kwargs)

    return decorated_function


def admin_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "You must log in as administrator."
            )
            return redirect("/admin/login")

        if session.get("user_role") != "admin":
            flash(
                "You do not have administrator permission."
            )
            return redirect("/")

        return function(*args, **kwargs)

    return decorated_function