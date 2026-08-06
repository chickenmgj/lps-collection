from flask import render_template, request

from flask_app import app
from flask_app.models.lps import Lps


@app.route("/")
def home():
    counts = Lps.get_counts()

    return render_template(
        "index.html",
        counts=counts
    )


@app.route("/collection")
def collection():
    search = request.args.get("search", "").strip()
    generation = request.args.get("generation", "").strip()
    order = request.args.get("order", "priority").strip()

    lps_items = Lps.search_by_status({
        "status": "owned",
        "search": f"%{search}%",
        "generation": generation,
        "order": order
    })

    counts = Lps.get_counts()

    return render_template(
        "collection.html",
        lps_items=lps_items,
        counts=counts,
        search=search,
        selected_generation=generation,
        selected_order=order
    )


@app.route("/wishlist")
def wishlist():
    search = request.args.get("search", "").strip()
    generation = request.args.get("generation", "").strip()
    order = request.args.get("order", "priority").strip()

    lps_items = Lps.search_by_status({
        "status": "wishlist",
        "search": f"%{search}%",
        "generation": generation,
        "order": order
    })

    counts = Lps.get_counts()

    return render_template(
        "wishlist.html",
        lps_items=lps_items,
        counts=counts,
        search=search,
        selected_generation=generation,
        selected_order=order
    )


@app.route("/trade")
def trade():
    search = request.args.get("search", "").strip()
    generation = request.args.get("generation", "").strip()
    order = request.args.get("order", "priority").strip()

    lps_items = Lps.search_for_trade({
        "search": f"%{search}%",
        "generation": generation,
        "order": order
    })

    counts = Lps.get_counts()

    return render_template(
        "trade.html",
        lps_items=lps_items,
        counts=counts,
        search=search,
        selected_generation=generation,
        selected_order=order
    )