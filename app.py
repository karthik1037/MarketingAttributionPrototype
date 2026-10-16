
from flask import Flask, render_template, request, session
from database import initialize_database, save_visit
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


if __name__ == "__main__":
    app.run(debug=True)
