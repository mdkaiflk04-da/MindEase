"""
app.py - Flask app with Gemini AI integration
"""

from flask import Flask, render_template, request, jsonify, session
from chatbot import analyze_sentiment, analyze_conversation_sentiment
import csv, os, datetime, json, requests
from collections import Counter

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mindease-secret-2024")

LOG_FILE = "chat_log.csv"

SYSTEM_PROMPT = """You are MindEase, a warm, empathetic AI mental health companion.
- Listen deeply and respond with genuine empathy and care
- Ask thoughtful follow-up questions
- Use gentle, human language — never clinical or robotic
- Keep responses concise (2-4 sentences) unless more depth is needed
- Use emojis sparingly and only when natural
- Remember context from earlier in the conversation
If someone expresses crisis or suicidal thoughts:
- Respond with immediate warmth
- Encourage reaching out to trusted people or professionals
- Share: iCall India: 9152987821, Vandrevala Foundation: 1860-2662-345
Never give medical diagnoses or pretend to be a licensed therapist."""

# ── CSV ───────────────────────────────────────
def init_csv():
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["message", "sentiment", "timestamp"])
    except Exception:
        pass

def log_message(message, sentiment):
    try:
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([message, sentiment,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except Exception:
        pass

init_csv()

# ── GEMINI ────────────────────────────────────
def call_gemini(history):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set!")
        return "API key not configured. Please set GEMINI_API_KEY in environment variables."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

    # Build contents with system prompt embedded as first turn
    contents = [
        {"role": "user",  "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood. I am MindEase, ready to listen and support you with warmth and empathy."}]},
    ] + history

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 350,
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        data = resp.json()
        print("GEMINI STATUS:", resp.status_code)
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print("GEMINI ERROR BODY:", json.dumps(data))
            return "I'm having a moment of difficulty. Please try again shortly. 💙"
    except requests.exceptions.Timeout:
        print("GEMINI TIMEOUT")
        return "The response took too long. Please try again. 💙"
    except Exception as e:
        print("GEMINI EXCEPTION:", str(e))
        return "Something went wrong. Please try again. 💙"

# ── SESSION ───────────────────────────────────
def get_history():
    return session.get("history", [])

def save_history(history):
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

    history.append({"role": "user", "parts": [{"text": user_message}]})
    bot_response = call_gemini(history)
    history.append({"role": "model", "parts": [{"text": bot_response}]})
    save_history(history)

    msg_sentiment     = analyze_sentiment(user_message)
    overall_sentiment = analyze_conversation_sentiment(history)
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
