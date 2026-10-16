from flask import Flask, render_template, request, session, jsonify
from database import (
    initialize_database,
    save_visit,
    initialize_orders,
    save_order
)
import uuid

app = Flask(__name__)

# Development only. Replace with an environment secret
# before deploying the website publicly.
app.secret_key = "temporary-development-secret"

CHANNELS = {
    "paid_social": "Paid Social",
    "influencer": "Influencer Marketing",
    "word_of_mouth": "Word of Mouth",
    "farmers_market": "Farmers Markets / Pop-ups"
}

initialize_database()
initialize_orders()


@app.route("/")
def home():
    if "visitor_id" not in session:
        session["visitor_id"] = str(uuid.uuid4())

    source = request.args.get("utm_source", "").lower()

    channel = CHANNELS.get(source)

    # Record a touchpoint only when the URL contains
    # a recognized marketing channel.
    if channel:
        save_visit(session["visitor_id"], source)

    return render_template(
        "index.html",
        channel=channel,
        channels=CHANNELS
    )

PRODUCT_PRICES = {
    "Smoked Habanero": 1199,
    "Mango Scorpion": 1199,
    "Garlic Jalapeño": 1199,
    "Chipotle Honey": 1199,
    "3-Pack Sampler": 2999
}


@app.route("/checkout", methods=["POST"])
def checkout():
    visitor_id = session.get("visitor_id")

    if not visitor_id:
        return jsonify({
            "error": "Visit the homepage before checkout."
        }), 400

    data = request.get_json(silent=True) or {}
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({"error": "Cart is empty."}), 400

    if len(items) > 100:
        return jsonify({"error": "Too many items."}), 400

    total_cents = 0

    for item in items:
        if not isinstance(item, dict):
            return jsonify({"error": "Invalid item."}), 400

        name = item.get("name")

        if name not in PRODUCT_PRICES:
            return jsonify({
                "error": "Unknown product."
            }), 400

        total_cents += PRODUCT_PRICES[name]

    total_amount = total_cents / 100
    order_id = save_order(visitor_id, total_amount)

    return jsonify({
        "success": True,
        "order_id": order_id,
        "total": total_amount,
        "message": "Demo order saved successfully."
    })
if __name__ == "__main__":
    app.run(debug=True)
