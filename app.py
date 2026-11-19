
import os
import uuid

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    session,
    jsonify,
    send_file
)

from attribution import calculate_attribution
from excel_export import export_workbook
from google_sheets import sync_touchpoints

from database import (
    initialize_database,
    initialize_orders,
    add_survey_column,
    save_visit,
    save_order
)

from demo_checkout import (
    checkout_bp,
    initialize_demo_payments
)

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "temporary-development-secret"
)

# Initialize database once
initialize_database()
initialize_orders()
add_survey_column()

# Initialize payment system once
initialize_demo_payments()


# Register payment routes once
app.register_blueprint(checkout_bp)


CHANNELS = {
    "paid_social": "Paid Social",
    "influencer": "Influencer Marketing",
    "word_of_mouth": "Word of Mouth",
    "farmers_market": "Farmers Markets / Pop-ups"
}
PROMOTIONS = {
    "paid_social": {
        "message": "Welcome from our social media ad!",
        "code": "SOCIAL10",
        "description": "10% off your first order"
    },
    "influencer": {
        "message": "Welcome, friend of @chilichelle!",
        "code": "CHELLE10",
        "description": "10% off your first order"
    },
    "farmers_market": {
        "message": "Thanks for visiting our farmers market!",
        "code": "MARKET5",
        "description": "$5 off your order"
    },
    "word_of_mouth": {
        "message": "A friend recommended Bonfire Pepper Co.!",
        "code": "FRIEND",
        "description": "10% off your first order"
    }
}

initialize_database()
initialize_orders()

add_survey_column()



@app.route("/")
def home():
    if "visitor_id" not in session:
        session["visitor_id"] = str(uuid.uuid4())

    source = request.args.get("utm_source", "").lower()

    channel = CHANNELS.get(source)
    promotion = PROMOTIONS.get(source)

    # Record marketing touchpoint
    if channel:
        save_visit(session["visitor_id"], source)

        # Automatically sync to Google Sheets
        try:
            synced = sync_touchpoints()
            app.logger.info(
                "Google Sheets: %s new touchpoints synced",
                synced
            )
        except Exception:
            app.logger.exception(
                "Google Sheets sync failed. "
                "Visit remains saved in SQLite."
            )

    return render_template(
        "index.html",
        channel=channel,
        channels=CHANNELS,
        promotion=promotion
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
            "error": "Visit homepage before checkout."
        }), 400

    data = request.get_json(silent=True) or {}
    items = data.get("items")

    # Get survey answer
    survey_source = data.get("survey_source")

    ALLOWED_SURVEY_SOURCES = {
        "An Instagram or Facebook ad",
        "A creator or influencer",
        "A farmers market or pop-up",
        "A friend or family member",
        "Google search",
        "Other"
    }

    if survey_source not in ALLOWED_SURVEY_SOURCES:
        survey_source = None

    # Validate cart
    if not isinstance(items, list) or not items:
        return jsonify({
            "error": "Cart is empty."
        }), 400

    if len(items) > 100:
        return jsonify({
            "error": "Too many items."
        }), 400

    # Calculate total
    total_cents = 0

    for item in items:
        if not isinstance(item, dict):
            return jsonify({
                "error": "Invalid cart item."
            }), 400

        product_name = item.get("name")

        if product_name not in PRODUCT_PRICES:
            return jsonify({
                "error": "Unknown product."
            }), 400

        total_cents += PRODUCT_PRICES[product_name]

    total_amount = total_cents / 100

    # Save order and survey answer
    order_id = save_order(
        visitor_id,
        total_amount,
        survey_source
    )

    return jsonify({
        "success": True,
        "order_id": order_id,
        "total": total_amount,
        "message": "Demo order saved successfully."
    })

    

@app.route("/api/attribution")
def attribution_api():
    return jsonify(calculate_attribution())


@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("dashboard.html")


# Excel export route
@app.route("/admin/export-excel")
def download_excel():
    excel_path = export_workbook()

    return send_file(
        excel_path,
        as_attachment=True,
        download_name="Marketing_Attribution_Report.xlsx"
    )


# Always keep this at the very bottom
if __name__ == "__main__":
    app.run(debug=True)

