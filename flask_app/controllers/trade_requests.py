import os
from datetime import datetime
from uuid import uuid4

from flask import flash, redirect, render_template, request, session
from werkzeug.utils import secure_filename

from flask_app import app
from flask_app.models.lps import Lps
from flask_app.models.trade_request import TradeRequest
from flask_app.utils.decorators import user_required


ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def save_trade_photo(photo):
    if not photo or not photo.filename:
        return None

    if not allowed_image(photo.filename):
        return None

    original_name = secure_filename(photo.filename)
    extension = original_name.rsplit(".", 1)[1].lower()

    unique_name = (
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}_"
        f"{uuid4().hex}.{extension}"
    )

    upload_folder = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "trade_requests"
    )

    os.makedirs(upload_folder, exist_ok=True)

    full_path = os.path.join(
        upload_folder,
        unique_name
    )

    photo.save(full_path)

    return f"uploads/trade_requests/{unique_name}"


@app.route("/trade/request/<string:lps_id>")
@user_required
def trade_request_form(lps_id):
    item = Lps.get_by_id({
        "id": lps_id
    })

    if not item:
        flash(
            "The selected LPS item was not found."
        )
        return redirect("/trade")

    if not item.trade:
        flash(
            "This item is not currently available for trade."
        )
        return redirect("/trade")

    has_completed_trade = (
        TradeRequest.user_has_completed_trade({
            "user_id": session["user_id"]
        })
    )

    is_first_trade = not has_completed_trade

    return render_template(
        "trade_request_form.html",
        item=item,
        is_first_trade=is_first_trade
    )


@app.route(
    "/trade/request/<string:lps_id>/create",
    methods=["POST"]
)
@user_required
def create_trade_request(lps_id):
    item = Lps.get_by_id({
        "id": lps_id
    })

    if not item:
        flash(
            "The selected LPS item was not found."
        )
        return redirect("/trade")

    if not item.trade:
        flash(
            "This item is not currently available for trade."
        )
        return redirect("/trade")

    instagram_username = request.form.get(
        "instagram_username",
        ""
    ).strip()

    offered_item = request.form.get(
        "offered_item",
        ""
    ).strip()

    item_condition = request.form.get(
        "item_condition",
        ""
    ).strip()

    proof_link = request.form.get(
        "proof_link",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()

    has_completed_trade = (
        TradeRequest.user_has_completed_trade({
            "user_id": session["user_id"]
        })
    )

    is_first_trade = not has_completed_trade

    first_trade_acceptance = request.form.get(
        "first_trade_send_first_accepted"
    )

    verification_photo = request.files.get(
        "verification_photo"
    )

    additional_photo_1 = request.files.get(
        "additional_photo_1"
    )

    additional_photo_2 = request.files.get(
        "additional_photo_2"
    )

    additional_photo_3 = request.files.get(
        "additional_photo_3"
    )

    is_valid = True

    if len(instagram_username) < 2:
        flash(
            "Please enter your Instagram username.",
            "trade_request"
        )
        is_valid = False

    if len(offered_item) < 3:
        flash(
            "Please describe what you are offering.",
            "trade_request"
        )
        is_valid = False

    if len(item_condition) < 10:
        flash(
            "Please describe the condition of the item.",
            "trade_request"
        )
        is_valid = False

    if is_first_trade and not first_trade_acceptance:
        flash(
            "Because this is your first trade, you must agree "
            "to send your package first.",
            "trade_request"
        )
        is_valid = False

    if (
        not verification_photo
        or not verification_photo.filename
    ):
        flash(
            "The verification photo is required.",
            "trade_request"
        )
        is_valid = False

    if (
        not additional_photo_1
        or not additional_photo_1.filename
    ):
        flash(
            "At least one additional photo is required.",
            "trade_request"
        )
        is_valid = False

    photos = [
        verification_photo,
        additional_photo_1,
        additional_photo_2,
        additional_photo_3
    ]

    for photo in photos:
        if photo and photo.filename:
            if not allowed_image(photo.filename):
                flash(
                    "Photos must be PNG, JPG, JPEG or WEBP.",
                    "trade_request"
                )
                is_valid = False
                break

    if not is_valid:
        return redirect(
            f"/trade/request/{lps_id}"
        )

    verification_path = save_trade_photo(
        verification_photo
    )

    additional_path_1 = save_trade_photo(
        additional_photo_1
    )

    additional_path_2 = save_trade_photo(
        additional_photo_2
    )

    additional_path_3 = save_trade_photo(
        additional_photo_3
    )

    if not verification_path or not additional_path_1:
        flash(
            "The required photos could not be saved.",
            "trade_request"
        )
        return redirect(
            f"/trade/request/{lps_id}"
        )

    TradeRequest.save({
        "user_id": session["user_id"],
        "lps_id": lps_id,
        "instagram_username": instagram_username,
        "offered_item": offered_item,
        "item_condition": item_condition,
        "proof_link": proof_link or None,
        "message": message or None,
        "first_trade_send_first_accepted": (
            1
            if is_first_trade and first_trade_acceptance
            else 0
        ),
        "was_first_trade": (
            1 if is_first_trade else 0
        ),
        "verification_photo": verification_path,
        "additional_photo_1": additional_path_1,
        "additional_photo_2": additional_path_2,
        "additional_photo_3": additional_path_3
    })

    flash(
        "Your trade request was sent successfully.",
        "success"
    )

    return redirect("/my-trade-requests")


@app.route("/my-trade-requests")
@user_required
def my_trade_requests():
    requests_list = TradeRequest.get_by_user_id({
        "user_id": session["user_id"]
    })

    return render_template(
        "my_trade_requests.html",
        trade_requests=requests_list
    )


@app.route(
    "/my-trade-requests/<int:request_id>/cancel",
    methods=["POST"]
)
@user_required
def cancel_trade_request(request_id):
    TradeRequest.delete_pending_by_user({
        "id": request_id,
        "user_id": session["user_id"]
    })

    flash(
        "The pending trade request was cancelled.",
        "success"
    )

    return redirect("/my-trade-requests")


@app.route(
    "/my-trade-requests/<int:request_id>/shipping",
    methods=["POST"]
)
@user_required
def update_user_trade_shipping(request_id):
    trade_request = TradeRequest.get_by_id({
        "id": request_id
    })

    if not trade_request:
        flash(
            "Trade request not found.",
            "trade_request"
        )
        return redirect("/my-trade-requests")

    if trade_request.user_id != session["user_id"]:
        flash(
            "You do not have permission to update this request.",
            "trade_request"
        )
        return redirect("/my-trade-requests")

    if trade_request.status not in {
        "accepted",
        "admin_shipped",
        "user_shipped",
        "both_shipped"
    }:
        flash(
            "Shipping information can only be added "
            "after the request is accepted.",
            "trade_request"
        )
        return redirect("/my-trade-requests")

    shipping_company = request.form.get(
        "user_shipping_company",
        ""
    ).strip()

    tracking_number = request.form.get(
        "user_tracking_number",
        ""
    ).strip()

    tracking_url = request.form.get(
        "user_tracking_url",
        ""
    ).strip()

    shipping_note = request.form.get(
        "user_shipping_note",
        ""
    ).strip()

    package_photo = request.files.get(
        "user_package_photo"
    )

    is_valid = True

    if len(shipping_company) < 2:
        flash(
            "Please enter the shipping company.",
            "trade_request"
        )
        is_valid = False

    if len(tracking_number) < 3:
        flash(
            "Please enter the tracking number.",
            "trade_request"
        )
        is_valid = False

    if not package_photo or not package_photo.filename:
        flash(
            "A package photo is required.",
            "trade_request"
        )
        is_valid = False

    elif not allowed_image(package_photo.filename):
        flash(
            "Package photo must be PNG, JPG, JPEG or WEBP.",
            "trade_request"
        )
        is_valid = False

    if not is_valid:
        return redirect("/my-trade-requests")

    package_photo_path = save_trade_photo(
        package_photo
    )

    if not package_photo_path:
        flash(
            "The package photo could not be saved.",
            "trade_request"
        )
        return redirect("/my-trade-requests")

    TradeRequest.update_user_shipping({
        "id": request_id,
        "user_id": session["user_id"],
        "user_shipping_company": shipping_company,
        "user_tracking_number": tracking_number,
        "user_tracking_url": tracking_url or None,
        "user_shipping_note": shipping_note or None,
        "user_package_photo": package_photo_path
    })

    flash(
        "Your shipping information was saved successfully.",
        "success"
    )

    return redirect("/my-trade-requests")