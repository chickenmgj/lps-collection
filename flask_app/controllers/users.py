from flask import flash, redirect, render_template, request, session

from flask_app import app, bcrypt
from flask_app.models.user import User


@app.route("/register")
def user_register_form():
    if "user_id" in session:
        return redirect("/")

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def user_register():
    first_name = request.form.get("first_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    is_valid = True

    if len(first_name) < 2:
        flash("Name must contain at least 2 characters.", "register")
        is_valid = False

    if not email or "@" not in email:
        flash("Please enter a valid email address.", "register")
        is_valid = False

    if len(password) < 8:
        flash(
            "Password must contain at least 8 characters.",
            "register"
        )
        is_valid = False

    if password != confirm_password:
        flash("Passwords do not match.", "register")
        is_valid = False

    existing_user = User.get_by_email({
        "email": email
    })

    if existing_user:
        flash(
            "An account already exists with this email.",
            "register"
        )
        is_valid = False

    if not is_valid:
        return redirect("/register")

    encrypted_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    user_id = User.save({
        "first_name": first_name,
        "email": email,
        "password": encrypted_password,
        "role": "user"
    })

    session["user_id"] = user_id
    session["user_name"] = first_name
    session["user_role"] = "user"

    flash("Your account was created successfully.", "success")

    return redirect("/")


@app.route("/login")
def user_login_form():
    if "user_id" in session:
        return redirect("/")

    return render_template("user_login.html")


@app.route("/login", methods=["POST"])
def user_login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.get_by_email({
        "email": email
    })

    if not user:
        flash("Invalid email or password.", "login")
        return redirect("/login")

    if not bcrypt.check_password_hash(user.password, password):
        flash("Invalid email or password.", "login")
        return redirect("/login")

    if user.role != "user":
        flash(
            "Administrator accounts must use the admin login.",
            "login"
        )
        return redirect("/login")

    session["user_id"] = user.id
    session["user_name"] = user.first_name
    session["user_role"] = user.role

    return redirect("/")


@app.route("/logout")
def user_logout():
    session.clear()
    return redirect("/")