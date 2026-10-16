
from flask import Flask, render_template, request

app = Flask(__name__)

CHANNELS = {
    "paid_social": "Paid Social",
    "influencer": "Influencer Marketing",
    "word_of_mouth": "Word of Mouth",
    "farmers_market": "Farmers Markets / Pop-ups"
}

@app.route("/")
def home():
    source = request.args.get("utm_source", "")
    channel = CHANNELS.get(source)

    return render_template(
        "index.html",
        channel=channel,
        channels=CHANNELS
    )

if __name__ == "__main__":
    app.run(debug=True)
