import os
from datetime import datetime
from uuid import uuid4

from flask import flash, redirect, render_template, request, session
from werkzeug.utils import secure_filename

from flask_app import app, bcrypt
from flask_app.models.lps import Lps
from flask_app.models.trade_request import TradeRequest
from flask_app.models.user import User
from flask_app.utils.decorators import admin_required


ALLOWED_PACKAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_package_photo(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_PACKAGE_EXTENSIONS
    )


def save_admin_package_photo(photo):
    if not photo or not photo.filename:
        return None

    if not allowed_package_photo(photo.filename):
        return None

    original_name = secure_filename(photo.filename)
    extension = original_name.rsplit(".", 1)[1].lower()

    unique_name = (
        f"admin_{datetime.now().strftime('%Y%m%d%H%M%S')}_"
        f"{uuid4().hex}.{extension}"
    )

    upload_folder = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "trade_shipping"
    )

    os.makedirs(upload_folder, exist_ok=True)

    full_path = os.path.join(
        upload_folder,
        unique_name
    )

    photo.save(full_path)

    return f"uploads/trade_shipping/{unique_name}"


@app.route("/admin/register")
@admin_required
def admin_register_form():
    return render_template("register_admin.html")


@app.route("/admin/register", methods=["POST"])
@admin_required
def admin_register():
    first_name = request.form["first_name"].strip()
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    is_valid = True

    if len(first_name) < 2:
        flash("Name must contain at least 2 characters.")
        is_valid = False

    if len(password) < 8:
        flash("Password must contain at least 8 characters.")
        is_valid = False

    if password != confirm_password:
        flash("Passwords do not match.")
        is_valid = False

    existing_user = User.get_by_email({
        "email": email
    })

    if existing_user:
        flash("An account already exists with this email.")
        is_valid = False

    if not is_valid:
        return redirect("/admin/register")

    encrypted_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    user_id = User.save({
        "first_name": first_name,
        "email": email,
        "password": encrypted_password,
        "role": "admin"
    })

    session["user_id"] = user_id
    session["user_name"] = first_name
    session["user_role"] = "admin"

    return redirect("/")


@app.route("/admin/login")
def admin_login_form():
    if "user_id" in session:
        return redirect("/")

    return render_template("login.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    user = User.get_by_email({
        "email": email
    })

    if not user:
        flash("Invalid email or password.")
        return redirect("/admin/login")

    if not bcrypt.check_password_hash(
        user.password,
        password
    ):
        flash("Invalid email or password.")
        return redirect("/admin/login")

    if user.role != "admin":
        flash(
            "This account does not have administrator access."
        )
        return redirect("/admin/login")

    session["user_id"] = user.id
    session["user_name"] = user.first_name
    session["user_role"] = user.role

    return redirect("/")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/")


@app.route("/admin")
@admin_required
def admin_dashboard():
    lps_items = Lps.get_all()

    return render_template(
        "admin_dashboard.html",
        lps_items=lps_items
    )


@app.route("/admin/lps/new")
@admin_required
def new_lps_form():
    return render_template("new_lps.html")


@app.route("/admin/lps/create", methods=["POST"])
@admin_required
def create_lps():
    lps_id = request.form["id"].strip().lower()
    name = request.form["name"].strip()
    generation = request.form["generation"]
    category = request.form["category"].strip()
    year = request.form.get("year")
    species = request.form.get(
        "species",
        ""
    ).strip()
    image = request.form["image"].strip()
    status = request.form["status"]

    is_valid = True

    if len(lps_id) < 2:
        flash(
            "LPS ID must contain at least 2 characters."
        )
        is_valid = False

    if len(name) < 2:
        flash(
            "Name must contain at least 2 characters."
        )
        is_valid = False

    existing_lps = Lps.get_by_id({
        "id": lps_id
    })

    if existing_lps:
        flash(
            "An LPS item with this ID already exists."
        )
        is_valid = False

    if not is_valid:
        return redirect("/admin/lps/new")

    Lps.save({
        "id": lps_id,
        "name": name,
        "generation": generation,
        "category": category,
        "year": int(year) if year else None,
        "species": species or None,
        "image": image,
        "status": status,
        "priority": (
            1 if request.form.get("priority") else 0
        ),
        "favorite": (
            1 if request.form.get("favorite") else 0
        ),
        "trade": (
            1 if request.form.get("trade") else 0
        )
    })

    flash("LPS item added successfully.")

    return redirect("/admin")


@app.route("/admin/lps/<string:lps_id>/edit")
@admin_required
def edit_lps_form(lps_id):
    item = Lps.get_by_id({
        "id": lps_id
    })

    if not item:
        flash("LPS item not found.")
        return redirect("/admin")

    return render_template(
        "edit_lps.html",
        item=item
    )


@app.route(
    "/admin/lps/<string:lps_id>/update",
    methods=["POST"]
)
@admin_required
def update_lps(lps_id):
    name = request.form["name"].strip()
    generation = request.form["generation"]
    category = request.form["category"].strip()
    year = request.form.get("year")
    species = request.form.get(
        "species",
        ""
    ).strip()
    image = request.form["image"].strip()
    status = request.form["status"]

    if len(name) < 2:
        flash(
            "Name must contain at least 2 characters."
        )
        return redirect(
            f"/admin/lps/{lps_id}/edit"
        )

    Lps.update({
        "id": lps_id,
        "name": name,
        "generation": generation,
        "category": category,
        "year": int(year) if year else None,
        "species": species or None,
        "image": image,
        "status": status,
        "priority": (
            1 if request.form.get("priority") else 0
        ),
        "favorite": (
            1 if request.form.get("favorite") else 0
        ),
        "trade": (
            1 if request.form.get("trade") else 0
        )
    })

    flash("LPS item updated successfully.")

    return redirect("/admin")


@app.route(
    "/admin/lps/<string:lps_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_lps(lps_id):
    item = Lps.get_by_id({
        "id": lps_id
    })

    if not item:
        flash("LPS item not found.")
        return redirect("/admin")

    Lps.delete({
        "id": lps_id
    })

    flash("LPS item deleted successfully.")

    return redirect("/admin")


@app.route("/admin/trade-requests")
@admin_required
def admin_trade_requests():
    trade_requests = TradeRequest.get_all()

    return render_template(
        "admin_trade_requests.html",
        trade_requests=trade_requests
    )


@app.route(
    "/admin/trade-requests/<int:request_id>/status",
    methods=["POST"]
)
@admin_required
def update_trade_request_status(request_id):
    allowed_statuses = {
        "pending",
        "accepted",
        "rejected",
        "more_info",
        "completed"
    }

    status = request.form.get(
        "status",
        ""
    ).strip()

    if status not in allowed_statuses:
        flash(
            "Invalid trade request status."
        )
        return redirect(
            "/admin/trade-requests"
        )

    trade_request = TradeRequest.get_by_id({
        "id": request_id
    })

    if not trade_request:
        flash(
            "Trade request not found."
        )
        return redirect(
            "/admin/trade-requests"
        )

    TradeRequest.update_status({
        "id": request_id,
        "status": status
    })

    flash(
        "Trade request status updated successfully."
    )

    return redirect(
        "/admin/trade-requests"
    )


@app.route(
    "/admin/trade-requests/<int:request_id>/shipping",
    methods=["POST"]
)
@admin_required
def update_admin_trade_shipping(request_id):
    trade_request = TradeRequest.get_by_id({
        "id": request_id
    })

    if not trade_request:
        flash(
            "Trade request not found."
        )
        return redirect(
            "/admin/trade-requests"
        )

    shipping_company = request.form.get(
        "admin_shipping_company",
        ""
    ).strip()

    tracking_number = request.form.get(
        "admin_tracking_number",
        ""
    ).strip()

    tracking_url = request.form.get(
        "admin_tracking_url",
        ""
    ).strip()

    shipping_note = request.form.get(
        "admin_shipping_note",
        ""
    ).strip()

    package_photo = request.files.get(
        "admin_package_photo"
    )

    is_valid = True

    if len(shipping_company) < 2:
        flash(
            "Please enter the shipping company."
        )
        is_valid = False

    if len(tracking_number) < 3:
        flash(
            "Please enter the tracking number."
        )
        is_valid = False

    if (
        not package_photo
        or not package_photo.filename
    ):
        flash(
            "A package photo is required."
        )
        is_valid = False

    elif not allowed_package_photo(
        package_photo.filename
    ):
        flash(
            "Package photo must be PNG, JPG, JPEG or WEBP."
        )
        is_valid = False

    if not is_valid:
        return redirect(
            "/admin/trade-requests"
        )

    package_photo_path = save_admin_package_photo(
        package_photo
    )

    if not package_photo_path:
        flash(
            "The package photo could not be saved."
        )
        return redirect(
            "/admin/trade-requests"
        )

    TradeRequest.update_admin_shipping({
        "id": request_id,
        "admin_shipping_company": shipping_company,
        "admin_tracking_number": tracking_number,
        "admin_tracking_url": (
            tracking_url or None
        ),
        "admin_shipping_note": (
            shipping_note or None
        ),
        "admin_package_photo": package_photo_path
    })

    flash(
        "Your shipping information was saved successfully."
    )

    return redirect(
        "/admin/trade-requests"
    )
    
@app.route(
    "/admin/trade-requests/<int:request_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_completed_trade_request(request_id):
    trade_request = TradeRequest.get_by_id({
        "id": request_id
    })

    if not trade_request:
        flash("Trade request not found.")
        return redirect("/admin/trade-requests")

    if trade_request.status != "completed":
        flash(
            "Only completed trade requests can be deleted."
        )
        return redirect("/admin/trade-requests")

    TradeRequest.delete_completed({
        "id": request_id
    })

    flash(
        "Completed trade request deleted successfully."
    )

    return redirect("/admin/trade-requests")