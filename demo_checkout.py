
from flask import Blueprint, render_template

checkout_bp = Blueprint(
    "demo_checkout",
    __name__
)


def initialize_demo_payments():
    """Temporary setup for demo payments."""
    pass


@checkout_bp.route("/payment", methods=["GET"])
def payment_page():
    return render_template("payment.html")
