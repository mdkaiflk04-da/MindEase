"""
app.py - Flask app with Gemini AI integration
Routes: / (chat), /dashboard, /chat (POST), /clear (POST)
"""

from flask import Flask, render_template, request, jsonify, session
from chatbot import analyze_sentiment, analyze_conversation_sentiment
import csv, os, datetime, json, requests
from collections import Counter

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mindease-secret-2024")

# ── CONFIG ────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBN0UcMl3ji1waUAQ-7W9hZjT_Cog5gbLg")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
)

LOG_FILE = "chat_log.csv"

SYSTEM_PROMPT = """You are MindEase, a warm, empathetic AI mental health companion.

Your role:
- Listen deeply and respond with genuine empathy and care
- Ask thoughtful follow-up questions to understand the person better
- Offer supportive, non-judgmental responses
- Use gentle, human language — never clinical or robotic
- Keep responses concise (2-4 sentences usually) unless more depth is needed
- Use emojis sparingly and only when they feel natural
- Remember context from earlier in the conversation

If someone expresses crisis, suicidal thoughts, or severe distress:
- Respond with immediate warmth and care
- Gently encourage them to reach out to a trusted person or professional
- Share crisis resources: iCall India: 9152987821, Vandrevala Foundation: 1860-2662-345
- Never dismiss or minimize their feelings

Never:
- Give medical diagnoses
- Pretend to be a licensed therapist
- Use generic, copy-paste responses
- Be preachy or lecture the person"""

# ── CSV SETUP ─────────────────────────────────
def init_csv():
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["message", "sentiment", "timestamp"])
    except Exception:
        pass

def log_message(message: str, sentiment: str):
    try:
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                message, sentiment,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
    except Exception:
        pass

init_csv()

# ── GEMINI CALL ───────────────────────────────
def call_gemini(history: list) -> str:
    """Send conversation history to Gemini and return response text."""
    # Prepend system prompt as first user/model exchange for v1 compatibility
    full_history = [
        {"role": "user",  "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood. I'm MindEase, a warm and empathetic mental health companion. I'm ready to listen and support."}]},
    ] + history

    payload = {
        "contents": full_history,
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 300,
        }
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=15)
        data = resp.json()
        print("GEMINI RESPONSE:", data)
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print("GEMINI ERROR:", str(e), resp.text if 'resp' in locals() else "no response")
        return "I'm having a little trouble connecting right now. Please try again in a moment. 💙"

# ── SESSION HISTORY ───────────────────────────
def get_history():
    return session.get("history", [])

def save_history(history):
    # Keep last 20 turns to stay within token limits
    session["history"] = history[-40:]

# ── ROUTES ────────────────────────────────────
@app.route("/")
def index():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Empty message"}), 400

    user_message = data["message"].strip()
    history = get_history()

    # Add user message to history
    history.append({"role": "user", "parts": [{"text": user_message}]})

    # Get Gemini response
    bot_response = call_gemini(history)

    # Add bot response to history
    history.append({"role": "model", "parts": [{"text": bot_response}]})
    save_history(history)

    # Analyze sentiment across full conversation
    overall_sentiment = analyze_conversation_sentiment(history)
    msg_sentiment     = analyze_sentiment(user_message)

    # Log to CSV
    log_message(user_message, msg_sentiment)

    return jsonify({
        "response": bot_response,
        "sentiment": msg_sentiment,
        "overall_sentiment": overall_sentiment,
    })

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "ok"})

@app.route("/dashboard")
def dashboard():
    rows = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                rows = [r for r in csv.DictReader(f) if r.get("sentiment")]
    except Exception:
        rows = []

    total  = len(rows)
    counts = Counter(r["sentiment"] for r in rows)
    sentiment_data = {k: counts.get(k, 0) for k in ["positive","negative","neutral","crisis"]}

    daily = {}
    for r in rows:
        try:
            date = r["timestamp"][:10]
            daily.setdefault(date, {"positive":0,"negative":0,"neutral":0,"crisis":0})
            daily[date][r["sentiment"]] = daily[date].get(r["sentiment"], 0) + 1
        except Exception:
            pass

    labels = sorted(daily.keys())
    timeline_data = {k: [daily[d].get(k,0) for d in labels]
                     for k in ["positive","negative","neutral","crisis"]}
    most_common = max(sentiment_data, key=sentiment_data.get) if total else "—"

    return render_template("dashboard.html",
        total=total,
        sentiment_data=json.dumps(sentiment_data),
        timeline_labels=json.dumps(labels),
        timeline_data=json.dumps(timeline_data),
        recent=rows[-10:][::-1],
        most_common=most_common,
    )

if __name__ == "__main__":
    app.run(debug=False, port=5000)
