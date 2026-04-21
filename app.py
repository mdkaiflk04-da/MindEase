"""
app.py - Flask application entry point
Routes: / (index), /chat (POST API)
"""

from flask import Flask, render_template, request, jsonify
from chatbot import Memory, generate_response, analyze_sentiment
import csv
import os
import datetime
import json
from collections import Counter

app = Flask(__name__)

# Global memory instance (single-user session)
memory = Memory()

# ─────────────────────────────────────────────
#  CSV LOGGING SETUP
# ─────────────────────────────────────────────
LOG_FILE = "chat_log.csv"

def init_csv():
    """Create CSV with headers if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["message", "sentiment", "timestamp"])

def log_message(message: str, sentiment: str):
    """Append a chat message to the CSV log."""
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([message, sentiment, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    POST /chat
    Expects JSON: {"message": "..."}
    Returns JSON: {"response": "...", "sentiment": "..."}
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Analyze sentiment
    sentiment = analyze_sentiment(user_message)

    # Generate bot response
    bot_response = generate_response(user_message, memory)

    # Log to CSV
    log_message(user_message, sentiment)

    return jsonify({
        "response": bot_response,
        "sentiment": sentiment
    })


@app.route("/dashboard")
def dashboard():
    """Render the live analytics dashboard."""
    rows = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("sentiment")]

    total = len(rows)

    # Sentiment counts
    sentiments = [r["sentiment"] for r in rows]
    counts = Counter(sentiments)
    sentiment_data = {
        "positive": counts.get("positive", 0),
        "negative": counts.get("negative", 0),
        "neutral":  counts.get("neutral",  0),
        "crisis":   counts.get("crisis",   0),
    }

    # Sentiment over time (group by date)
    daily = {}
    for r in rows:
        try:
            date = r["timestamp"][:10]  # YYYY-MM-DD
            if date not in daily:
                daily[date] = {"positive": 0, "negative": 0, "neutral": 0, "crisis": 0}
            daily[date][r["sentiment"]] = daily[date].get(r["sentiment"], 0) + 1
        except Exception:
            pass

    timeline_labels = sorted(daily.keys())
    timeline_data = {
        "positive": [daily[d].get("positive", 0) for d in timeline_labels],
        "negative": [daily[d].get("negative", 0) for d in timeline_labels],
        "neutral":  [daily[d].get("neutral",  0) for d in timeline_labels],
        "crisis":   [daily[d].get("crisis",   0) for d in timeline_labels],
    }

    # Recent messages (last 10)
    recent = rows[-10:][::-1]

    most_common = max(sentiment_data, key=sentiment_data.get) if total > 0 else "—"

    return render_template("dashboard.html",
        total=total,
        sentiment_data=json.dumps(sentiment_data),
        timeline_labels=json.dumps(timeline_labels),
        timeline_data=json.dumps(timeline_data),
        recent=recent,
        most_common=most_common,
    )


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_csv()
    app.run(debug=True, port=5000)
