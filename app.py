"""
app.py - Flask application entry point
Routes: / (index), /chat (POST API)
"""

from flask import Flask, render_template, request, jsonify
from chatbot import Memory, generate_response, analyze_sentiment
import csv
import os
import datetime

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


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_csv()
    app.run(debug=True, port=5000)
